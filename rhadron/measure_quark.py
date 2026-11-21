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

from .backend import to_numpy
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


def source_sites(shape, cfg_id, n_src, seed=0):
    Lt, Lz, Ly, Lx = shape
    rng = np.random.default_rng([seed, cfg_id])
    t0 = int(rng.integers(Lt))
    sites = []
    for k in range(n_src):  # sources spread in time: t0 + k Lt / n_src, random spatial position
        t = (t0 + k * Lt // n_src) % Lt
        sites.append((int(rng.integers(Lx)), int(rng.integers(Ly)), int(rng.integers(Lz)), t))
    return sites


def _site_series(S, x0, tmax):
    x, y, z, t0 = x0
    Lt = S.shape[0]
    idx = [(t0 + t) % Lt for t in range(tmax + 1)]
    return to_numpy(S[idx, z, y, x])  # [tmax+1, 4, 3, 4, 3]


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
    sites = source_sites(shape, cfg_id, qcfg["n_src"], qcfg.get("seed", 0))
    W = {}
    for a in qcfg["static_actions"]:
        V4 = static_links(U, a)
        W[a] = [to_numpy(wilson_lines(V4, x0[3], tmax)[:, x0[2], x0[1], x0[0]]) for x0 in sites]
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
                    Ssm = _sink_smear(Usm, Ssrc, lev2)
                    out[(role, isrc, ilev, jlev)] = _site_series(Ssm, x0, tmax)
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
    import cupy as cp

    from .dirac import wuppertal

    Lx, Ly, Lz, Lt = li.global_size if hasattr(li, "global_size") else li.size
    S = cp.zeros((Lt, Lz, Ly, Lx, 4, 3, 4, 3), dtype=cp.complex128)
    for s0 in range(4):
        for a0 in range(3):
            b = cp.zeros((Lt, Lz, Ly, Lx, 4, 3), dtype=cp.complex128)
            b[x0[3], x0[2], x0[1], x0[0], s0, a0] = 1.0
            b = wuppertal(Usm, b, lev[0], lev[1])
            x = d.invert(Q._fermion_from_lexico(li, b))
            S[..., s0, a0] = Q.lexico_xp(cp.asarray(x.data), cp)
    return S


def _sink_smear(Usm, S, lev):
    from .dirac import wuppertal

    out = S.copy()
    for s0 in range(4):
        for a0 in range(3):
            out[..., s0, a0] = wuppertal(Usm, S[..., s0, a0], lev[0], lev[1])
    return out


def contract_all(site, sites, W, roles, smears, tmax, qcfg):
    """All static-site correlators, averaged over sources; matrix over (src level, snk level)."""
    nl = len(smears)
    light_role = qcfg.get("light_roles", [r for r in roles if r != "s"])
    corr = {}
    # light hadrons
    for k, v in site.items():
        if k[0] == "light":
            corr[f"light/{k[1]}/{k[2]}"] = np.mean(v, axis=0)
    for act, Wlist in W.items():
        for isrc, x0 in enumerate(sites):
            Wt = Wlist[isrc]
            for lr in light_role:
                # flavour assignment: u = d = light role lr, s = 's'
                for fl in MESON_FLAVOURS:
                    if "s" not in roles and "s" in fl:
                        continue
                    for gname, (gams, irrep, jp) in qo.MESON_GAMMAS.items():
                        key = f"{act}/rmeson/{lr}/{fl}/{gname}"
                        M = np.zeros((tmax + 1, nl, nl), dtype=complex)
                        for il in range(nl):
                            for jl in range(nl):
                                props = _props(site, lr, isrc, il, jl, roles)
                                c = 0
                                for Gam in gams:  # average rows of the irrep
                                    F = qo.meson_tensor(Gam, qo.flavour_matrix(fl))
                                    B = hadron.rmeson_block(F, qo.meson_bar(F), props, tmax)
                                    c = c + hadron.contract_rmeson(B, Wt)
                                M[:, jl, il] = c / len(gams)
                        corr[key] = corr.get(key, 0) + M / len(sites)
                # fundamental static-light (validation, M3)
                for gname, Gam in (("S_g5", qo.G5), ("Pm_1", qo.ONE), ("Pp_g5gi", qo.G5 @ G[0])):
                    key = f"{act}/staticlight/{lr}/{gname}"
                    M = np.zeros((tmax + 1, nl, nl), dtype=complex)
                    for il in range(nl):
                        for jl in range(nl):
                            M[:, jl, il] = hadron.static_light(Gam, site[(lr, isrc, il, jl)], Wt)
                    corr[key] = corr.get(key, 0) + M / len(sites)
                for (col, fla, dq, j) in BARYONS:
                    if "s" not in roles and ("uds" in fla):
                        continue
                    F = qo.baryon_tensor(col, fla, dq, j, nr=True)
                    Fb = qo.baryon_bar(F)
                    key = f"{act}/rbaryon/{lr}/{col}_{fla}_{dq}_{j.replace('/', 'o')}"
                    M = np.zeros((tmax + 1, nl, nl), dtype=complex)
                    for il in range(nl):
                        for jl in range(nl):
                            props = _props(site, lr, isrc, il, jl, roles)
                            B = hadron.rbaryon_block_fast(F, Fb, props, tmax)
                            Cb = hadron.contract_rbaryon(B, Wt)
                            M[:, jl, il] = np.einsum("trr->t", Cb) / Cb.shape[1]
                    corr[key] = corr.get(key, 0) + M / len(sites)
    return corr


def _props(site, lr, isrc, il, jl, roles):
    p = {0: site[(lr, isrc, il, jl)], 1: site[(lr, isrc, il, jl)]}
    if "s" in roles:
        p[2] = site[("s", isrc, il, jl)]
    return p
