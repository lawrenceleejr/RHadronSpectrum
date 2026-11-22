"""Quark-sector measurement for one configuration (GPU job payload).

For each source site x0 (deterministic per config) and each source smearing level:
  solve 12 columns per kappa (QUDA, clover, multigrid), sink-smear at every level, then
  * site propagators S(x0, t0+t; x0, t0), t = 0..tmax  ->  all static-site contractions on CPU:
      R-mesons (octet q qbar, all Gamma, flavour pairs), R-baryons (NR colour-octet qqq),
      fundamental static-light mesons (validation), with HYP2 (and HYP1) static lines
  * zero-momentum pi, rho, N from the point-sink (level 0 smearing at sink) propagator (M3)
Outputs one HDF5 per config with every correlator, attributes = provenance.
"""
import itertools
import time

import numpy as np

from .backend import get_xp, to_numpy
from .contract import hadron, light
from .gamma import G
from .operators import quark_ops as qo
from .static import static_links, wilson_lines

# R-baryon NR operator set: (colour, flavour, diquark, j); flavour names map to kappa roles below
BARYONS = [
    # Diquark exchange (q1 <-> q2): colour (octet_A: -, octet_S: +) x flavour x spin (Cg5: -, Cgi: +)
    # must be antisymmetric, otherwise the operator vanishes identically (checked in the unit tests).
    ("octet_A", "uud_A", "Cg5", "1/2"),       # (8, 1/2) octet  g~uud
    ("octet_S", "uud_A", "Cgi", "1/2"),       # (8, 1/2) octet, second colour structure
    ("octet_S", "uud_A", "Cgi", "3/2"),       # (8, 3/2)
    ("octet_A", "uud_S", "Cgi", "3/2"),       # (8, 3/2) ({ud} u: the decuplet j=3/2 part vanishes in NR)
    ("octet_A", "uuu", "Cgi", "1/2"),         # (10, 1/2) decuplet
    ("octet_A", "uds_singlet", "Cg5", "1/2"),  # (1, 1/2) flavour singlet (Farrar S0-like)
    ("octet_S", "uds_singlet", "Cgi", "1/2"),  # (1, 1/2) second colour structure
    ("octet_A", "uds_Lambda8", "Cg5", "1/2"),  # (8, 1/2) Lambda-like
]
MESON_FLAVOURS = ["ud", "us", "ss"]


def source_sites(shape, cfg_id, n_src, seed=0, pair_sep=None):
    """Deterministic source sites per configuration.
    pair_sep=None: n_src sources at random spatial positions, spread evenly in time.
    pair_sep=d:   n_src/2 random spatial positions, each with sources at t0 and t0 + d.  The pairs
    give both legs of three-point functions with an operator inserted between them at the same
    gluino site (charge/matter density of the light cloud; docs/visualization.md)."""
    Lt, Lz, Ly, Lx = shape
    rng = np.random.default_rng([seed, cfg_id])
    t0 = int(rng.integers(Lt))
    sites = []
    if pair_sep is None:
        for k in range(n_src):
            t = (t0 + k * Lt // n_src) % Lt
            sites.append((int(rng.integers(Lx)), int(rng.integers(Ly)), int(rng.integers(Lz)), t))
        return sites
    npair = max(1, n_src // 2)
    for k in range(npair):
        t = (t0 + k * Lt // npair) % Lt
        x = (int(rng.integers(Lx)), int(rng.integers(Ly)), int(rng.integers(Lz)))
        sites.append((*x, t))
        sites.append((*x, (t + pair_sep) % Lt))
    return sites


def _site_series(S, x0, tmax):
    x, y, z, t0 = x0
    Lt = S.shape[0]
    idx = [(t0 + t) % Lt for t in range(tmax + 1)]
    return S[idx, z, y, x].copy()  # [tmax+1, 4, 3, 4, 3] (stays on the device)


def run(U_np, qcfg, cfg_id, log=print):
    import cupy as cp

    from .gauge.smear import ape_spatial
    from .solve import quda as Q

    shape = U_np.shape[1:5]
    Lt, Lz, Ly, Lx = shape
    li = Q.init([Lx, Ly, Lz, Lt])
    gauge = Q.to_quda_gauge(li, U_np)
    U = cp.asarray(U_np)
    Usm = ape_spatial(U, qcfg["link_smear"]["alpha"], qcfg["link_smear"]["n"])
    tmax = qcfg["tmax"]
    sites = source_sites(shape, cfg_id, qcfg["n_src"], qcfg.get("seed", 0), qcfg.get("pair_sep"))
    W = {}
    for a in qcfg["static_actions"]:
        V4 = static_links(U, a)
        W[a] = [wilson_lines(V4, x0[3], tmax)[:, x0[2], x0[1], x0[0]].copy() for x0 in sites]
        del V4
    kappas = qcfg["kappas"]  # dict role -> kappa, roles: l1, l2, l3 (light), s
    roles = list(kappas)
    smears = qcfg["smear_levels"]  # list of (alpha, n)
    out, timings = {}, {}
    for role in roles:
        t0 = time.time()
        d = Q.make_dirac(li, gauge, kappas[role], qcfg["csw"], tol=qcfg["tol"], maxiter=qcfg["maxiter"],
                         multigrid=qcfg.get("multigrid"))
        timings[f"setup_{role}"] = time.time() - t0
        for isrc, x0 in enumerate(sites):
            for ilev, lev in enumerate(smears):
                t0 = time.time()
                # source-smeared solve; the unsmeared sink is used for the light hadrons
                Ssrc = _solve_smeared_source(Q, li, d, Usm, x0, lev)
                timings.setdefault(f"solve_{role}", []).append(time.time() - t0)
                for jlev, lev2 in enumerate(smears):
                    out[(role, isrc, ilev, jlev)] = _sink_smeared_site(Usm, Ssrc, x0, tmax, lev2)
                if ilev == 0:  # light hadrons: smeared source, point sink
                    for name, Gam in (("pi", qo.G5), ("rho", None), ("a0", qo.ONE)):
                        if Gam is None:
                            c = sum(light.meson(Ssrc, G[i], t0=x0[3]) for i in range(3)) / 3
                        else:
                            c = light.meson(Ssrc, Gam, t0=x0[3])
                        out.setdefault(("light", role, name), []).append(to_numpy(c))
                    out.setdefault(("light", role, "N"), []).append(to_numpy(light.nucleon(Ssrc, t0=x0[3])))
                del Ssrc
        if hasattr(d, "destroy"):
            d.destroy()
    corr = contract_all(out, sites, W, roles, smears, tmax, qcfg)
    for k, v in timings.items():
        timings[k] = float(np.sum(v))
    return corr, {"sites": sites, "timings": timings}


def _solve_smeared_source(Q, li, d, Usm, x0, lev):
    """12 solves with a Wuppertal-smeared point source at x0 (smearing on the source timeslice only)."""
    import cupy as cp

    from .dirac import wuppertal_cols

    Lx, Ly, Lz, Lt = li.global_size if hasattr(li, "global_size") else li.size
    x, y, z, t0 = x0
    col = cp.zeros((1, Lz, Ly, Lx, 3, 3), dtype=Usm.dtype)  # [.., a0, a]
    for a0 in range(3):
        col[0, z, y, x, a0, a0] = 1.0
    col = wuppertal_cols(Usm[:3, t0:t0 + 1], col, lev[0], lev[1]).astype(cp.complex128)
    S = cp.zeros((Lt, Lz, Ly, Lx, 4, 3, 4, 3), dtype=cp.complex128)
    for s0 in range(4):
        for a0 in range(3):
            b = cp.zeros((Lt, Lz, Ly, Lx, 4, 3), dtype=cp.complex128)
            b[t0, :, :, :, s0, :] = col[0, :, :, :, a0, :]
            sol = d.invert(Q._fermion_from_lexico(li, b))
            S[..., s0, a0] = Q.lexico_xp(cp.asarray(sol.data), cp)
    return S


def _sink_smeared_site(Usm, S, x0, tmax, lev):
    """Sink-smear S on the timeslices t0..t0+tmax only and return the site series [tmax+1, 4,3,4,3]."""
    from .dirac import wuppertal_cols

    cp = get_xp(S)

    x, y, z, t0 = x0
    Lt = S.shape[0]
    idx = [(t0 + t) % Lt for t in range(tmax + 1)]
    sub = cp.ascontiguousarray(S[idx].transpose(0, 1, 2, 3, 4, 6, 7, 5)).astype(Usm.dtype)  # colour last
    sub = wuppertal_cols(Usm[:3, idx], sub, lev[0], lev[1])
    return sub[:, z, y, x].transpose(0, 1, 4, 2, 3).astype(S.dtype)  # -> [t, s, a, s0, a0]


def contract_all(site, sites, W, roles, smears, tmax, qcfg):
    """All static-site correlators, averaged over sources; matrix [t, snk level, src level].
    Quark blocks (independent of the static action) are computed once and contracted with every
    static line in W = {action: [W(source) [t,3,3]]}."""
    nl = len(smears)
    light_roles = qcfg.get("light_roles", [r for r in roles if r != "s"])
    acts = list(W)
    corr = {}
    for k, v in site.items():
        if k[0] == "light":
            corr[f"light/{k[1]}/{k[2]}"] = np.mean([to_numpy(x) for x in v], axis=0)
    xp = get_xp(next(iter(v for k, v in site.items() if k[0] != "light")))
    mes_ops = {}
    for fl in MESON_FLAVOURS:
        if "s" in fl and "s" not in roles:
            continue
        for gname, (gams, irrep, jp) in qo.MESON_GAMMAS.items():
            Fs = [qo.meson_tensor(Gm, qo.flavour_matrix(fl)) for Gm in gams]
            mes_ops[(fl, gname)] = [(xp.asarray(F), xp.asarray(qo.meson_bar(F))) for F in Fs]
    bar_ops = {}
    for op in BARYONS:
        if "uds" in op[1] and "s" not in roles:
            continue
        F = qo.baryon_tensor(*op, nr=True)
        bar_ops[op] = (hadron.flavour_components(F), hadron.flavour_components(qo.baryon_bar(F)))

    def acc(key, il, jl, c):
        M = corr.setdefault(key, np.zeros((tmax + 1, nl, nl), dtype=complex))
        M[:, jl, il] += to_numpy(c) / len(sites)

    for isrc in range(len(sites)):
        for lr in light_roles:
            for il in range(nl):
                for jl in range(nl):
                    props = _props(site, lr, isrc, il, jl, roles)
                    for (fl, gname), FF in mes_ops.items():
                        Bs = [hadron.rmeson_block(F, Fb, props, tmax) for F, Fb in FF]
                        for a in acts:
                            c = sum(hadron.contract_rmeson(B, W[a][isrc]) for B in Bs) / len(Bs)
                            acc(f"{a}/rmeson/{lr}/{fl}/{gname}", il, jl, c)
                    for gname, Gam in (("S_g5", qo.G5), ("Pm_1", qo.ONE), ("Pp_g5gi", qo.G5 @ G[0])):
                        for a in acts:
                            c = hadron.static_light(Gam, site[(lr, isrc, il, jl)], W[a][isrc])
                            acc(f"{a}/staticlight/{lr}/{gname}", il, jl, c)
                    for op, (F, Fb) in bar_ops.items():
                        B = hadron.rbaryon_block_fast(F, Fb, props, tmax)
                        name = f"{op[0]}_{op[1]}_{op[2]}_{op[3].replace('/', 'o')}"
                        for a in acts:
                            Cb = hadron.contract_rbaryon(B, W[a][isrc])
                            acc(f"{a}/rbaryon/{lr}/{name}", il, jl, xp.einsum("trr->t", Cb) / Cb.shape[1])
    return corr


def _props(site, lr, isrc, il, jl, roles):
    p = {0: site[(lr, isrc, il, jl)], 1: site[(lr, isrc, il, jl)]}
    if "s" in roles:
        p[2] = site[("s", isrc, il, jl)]
    return p


# ------------------------------------------------------------------------------------------------
# Two-stage production: solve (one job per config and kappa role, GPU/QUDA) -> contract (per config).
def solve_role(U_np, qcfg, cfg_id, role, outpath, n_src=None, log=print):
    """Solve for one kappa role, all sources and smearing levels; store site propagators
    S(x0, t0+t; x0, t0) [tmax+1, 4, 3, 4, 3] per (source, src level, snk level) and light-hadron
    correlators.  Resumable: sources already in `outpath` are skipped; file rewritten atomically
    after every source."""
    import json as _json
    import os as _os

    import cupy as cp
    import h5py

    from .gauge.smear import ape_spatial
    from .solve import quda as Q

    shape = U_np.shape[1:5]
    Lt, Lz, Ly, Lx = shape
    tmax = qcfg["tmax"]
    smears = qcfg["smear_levels"]
    sites = source_sites(shape, cfg_id, qcfg["n_src"], qcfg.get("seed", 0), qcfg.get("pair_sep"))[: (n_src or qcfg["n_src"])]
    done = {}
    if _os.path.exists(outpath):
        with h5py.File(outpath, "r") as f:
            f.visititems(lambda name, obj: done.__setitem__(name, obj[...]) if isinstance(obj, h5py.Dataset) else None)
    t_all = time.time()

    def lap(msg, t):
        cp.cuda.Device().synchronize()
        log(f"[{role}] {msg}: {time.time() - t:.1f}s", flush=True)
        return time.time()

    t = time.time()
    li = Q.init([Lx, Ly, Lz, Lt])
    t = lap("quda init", t)
    gauge = Q.to_quda_gauge(li, U_np)
    t = lap("gauge to quda layout", t)
    # Smearing defines the interpolating operators only: single precision (complex64) is ample and
    # ~30x faster on low-FP64 GPUs (A40 / RTX); solves (QUDA mixed) and contractions stay double.
    U = cp.asarray(U_np)
    Usm = ape_spatial(U.astype(cp.complex64), qcfg["link_smear"]["alpha"], qcfg["link_smear"]["n"])
    t = lap("APE link smearing (fp32)", t)
    dens = bool(qcfg.get("densities")) and qcfg.get("pair_sep")
    if dens:
        from .contract.density import density_3pt

        V4 = static_links(U, "HYP2")
        sep = int(qcfg["pair_sep"])
        tau_off = sep // 2
        t = lap("HYP2 static links (densities)", t)
    t0 = time.time()
    d = Q.make_dirac(li, gauge, qcfg["kappas"][role], qcfg["csw"], tol=qcfg["tol"], maxiter=qcfg["maxiter"],
                     multigrid=qcfg.get("multigrid") if not qcfg.get("no_multigrid") else None)
    log(f"[{role}] dirac + MG setup {time.time() - t0:.1f}s", flush=True)
    for isrc, x0 in enumerate(sites):
        if f"src{isrc}/S_0_0" in done or f"src{isrc}" in {k.split('/')[0] for k in done}:
            log(f"[{role}] source {isrc} already done", flush=True)
            continue
        for il, lev in enumerate(smears):
            t1 = time.time()
            Ssrc = _solve_smeared_source(Q, li, d, Usm, x0, lev)
            cp.cuda.Device().synchronize()
            log(f"[{role}] src {isrc} level {il}: 12 solves {time.time() - t1:.1f}s", flush=True)
            t = time.time()
            for jl, lev2 in enumerate(smears):
                done[f"src{isrc}/S_{il}_{jl}"] = to_numpy(_sink_smeared_site(Usm, Ssrc, x0, tmax, lev2))
            t = lap("sink smearing", t)
            if il == 0 and dens:
                pair, member = divmod(isrc, 2)
                tau = (sites[2 * pair][3] + tau_off) % Lt
                done[f"src{isrc}/slice_tau"] = to_numpy(Ssrc[tau].reshape(-1, 4, 3, 4, 3))
                if member == 1:
                    x0 = sites[2 * pair]
                    Sy0 = cp.asarray(done[f"src{2 * pair}/slice_tau"])
                    Sy1 = Ssrc[tau].reshape(-1, 4, 3, 4, 3)
                    S10 = cp.asarray(done[f"src{2 * pair}/S_0_0"][sep])  # S(x1 <- x0), smeared both ends
                    Wl = wilson_lines(V4, x0[3], sep)[sep, x0[2], x0[1], x0[0]]
                    for cname, Gam in (("g5", qo.G5), ("gx", G[0])):
                        for jname, GJ in (("g4", G[3]), ("1", qo.ONE)):
                            cq, cqb = density_3pt(Sy0, Sy1, S10, Wl, Gam, GJ)
                            done[f"pair{pair}/dens_{cname}_{jname}_q"] = to_numpy(cq).reshape(Lz, Ly, Lx)
                            done[f"pair{pair}/dens_{cname}_{jname}_qbar"] = to_numpy(cqb).reshape(Lz, Ly, Lx)
                    del done[f"src{2 * pair}/slice_tau"], done[f"src{isrc}/slice_tau"]
                    t = lap(f"densities pair {pair}", t)
            if il == 0:
                done[f"src{isrc}/light_pi"] = to_numpy(light.meson(Ssrc, qo.G5, t0=x0[3]))
                done[f"src{isrc}/light_rho"] = to_numpy(sum(light.meson(Ssrc, G[i], t0=x0[3]) for i in range(3)) / 3)
                done[f"src{isrc}/light_a0"] = to_numpy(light.meson(Ssrc, qo.ONE, t0=x0[3]))
                t = lap("light mesons", t)
                done[f"src{isrc}/light_N"] = to_numpy(light.nucleon(Ssrc, t0=x0[3]))
                t = lap("nucleon", t)
            del Ssrc
        tmp = outpath + ".tmp"
        with h5py.File(tmp, "w") as f:
            for k, v in done.items():
                f.create_dataset(k, data=v)
            f.attrs["role"] = role
            f.attrs["kappa"] = qcfg["kappas"][role]
            f.attrs["sites"] = _json.dumps(sites)
            f.attrs["cfg_id"] = cfg_id
        _os.replace(tmp, outpath)
        log(f"[{role}] source {isrc} saved ({time.time() - t_all:.0f}s elapsed)", flush=True)
    return outpath


def contract_from_files(U_np, qcfg, role_files, log=print):
    """Combine the per-role site propagators of one configuration into all static-site correlators."""
    import json as _json

    import h5py

    try:
        import cupy as cp
        xp = cp
    except Exception:  # noqa: BLE001
        xp = np
    tmax = qcfg["tmax"]
    smears = qcfg["smear_levels"]
    site, sites, roles = {}, None, []
    for path in role_files:
        with h5py.File(path, "r") as f:
            role = str(f.attrs["role"])
            roles.append(role)
            sites = _json.loads(f.attrs["sites"])
            keys = []
            f.visititems(lambda name, obj: keys.append(name) if isinstance(obj, h5py.Dataset) else None)
            for k in keys:
                src, name = k.split("/")
                if not src.startswith("src"):
                    continue  # pair*/dens_* (density maps) are analysed separately
                isrc = int(src[3:])
                if name.startswith("S_"):
                    il, jl = map(int, name[2:].split("_"))
                    site[(role, isrc, il, jl)] = xp.asarray(f[k][...])
                elif name.startswith("light_"):
                    site.setdefault(("light", role, name[6:]), []).append(f[k][...])
    nsrc = min(len({k[1] for k in site if k[0] == r}) for r in roles)
    sites = sites[:nsrc]
    U = xp.asarray(U_np)
    W = {}
    for a in qcfg["static_actions"]:
        V4 = static_links(U, a)
        W[a] = [wilson_lines(V4, x0[3], tmax)[:, x0[2], x0[1], x0[0]].copy() for x0 in sites]
        del V4
    t0 = time.time()
    corr = contract_all(site, sites, W, roles, smears, tmax, qcfg)
    log(f"contractions {time.time() - t0:.0f}s for {nsrc} sources", flush=True)
    return corr, {"sites": sites, "roles": roles}
