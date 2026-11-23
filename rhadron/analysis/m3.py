"""M3 gate: light hadrons and fundamental static-light splittings on quenched β = 6.0 (qA60).

Light hadrons (per κ): AIC-averaged single-exponential fits of the zero-momentum π, ρ, N correlators
(smeared source, point sink, averaged over the 8 sources per configuration), compared to UKQCD
hep-lat/9910022 32³×64 (docs/references.md).  Static-light: GEVP (2 smearing levels) principal
correlators for S (γ5) and P₋ (Γ = 1; and γ5γ_x as the degenerate heavy-spin partner, a static-limit
check); P₋ − S per κ from correlated jackknife differences, chirally extrapolated linearly in
(a m_π)² and compared to BGR 0809.1103 (quenched) 435(15)(9) MeV.  a⁻¹ from r0 = 0.5 fm, r0/a = 5.369.
"""
import glob
import json
import os

import h5py
import numpy as np

from ..apbc import site_series_signs
from .gluelump import aic_weights, binned, fit_windows, plateau_onset, principal_correlator

UKQCD = {  # a m_pi, a m_V, a m_N (32^3 x 64), asymmetric errors symmetrised (max)
    "l1": {"kappa": 0.13344, "pi": (0.3952, 0.0016), "rho": (0.5400, 0.0047), "N": (0.799, 0.010)},
    "l2": {"kappa": 0.13417, "pi": (0.3048, 0.0013), "rho": (0.4887, 0.0061), "N": (0.700, 0.015)},
    "l3": {"kappa": 0.13455, "pi": (0.2457, 0.0014), "rho": (0.4636, 0.0088), "N": (0.641, 0.020)},
}
BGR_PM_S = (435.0, np.hypot(15, 9))
BGR_STATIC_STRANGE = {"PpE": (400.0, np.hypot(8, 8)), "PmD": (412.0, np.hypot(10, 8))}  # 0809.1103 Tab. 11
R0A, R0_FM, HBARC = 5.369, 0.5, 197.327


def ainv_mev():
    return R0A * HBARC / R0_FM


EXCLUDE = set()  # (stream, cfg) excluded as exceptional (set by run(exclude_exceptional=True))


def exceptional_configs(files, roles=("l1", "l2", "l3", "s"), t=10, factor=10.0):
    """Data-quality rule (proposed, logbook): a configuration is exceptional for the quenched valence
    sector if its pion correlator at t = 10 exceeds the median over configurations by > 10x for any kappa."""
    bad = set()
    for role in roles:
        rows = []
        for f in files:
            with h5py.File(f, "r") as h:
                k = f"light/{role}/pi"
                if k in h:
                    rows.append(((int(h.attrs["stream"]), int(h.attrs["cfg"])), float(h[k][t].real)))
        med = np.median([v for _, v in rows])
        bad |= {sc for sc, v in rows if v > factor * med}
    return bad


def load(files, key):
    rows = []
    for f in files:
        with h5py.File(f, "r") as h:
            if key in h and (int(h.attrs["stream"]), int(h.attrs["cfg"])) not in EXCLUDE:
                rows.append((int(h.attrs["stream"]), int(h.attrs["cfg"]), h[key][...]))
    rows.sort(key=lambda r: (r[0], r[1]))
    meta = [(r[0], r[1], 0.0) for r in rows]
    return np.array([r[2] for r in rows]), meta


def energy_jk(c, meta, binsize, t0, tmax, onset=True):
    pc = binned(c.real, meta, binsize)
    tfl = plateau_onset(pc, t0 + 1, tmax) if onset else None
    wins = fit_windows(pc, t0, tmax, tmin_floor=tfl)
    if not wins:
        return None
    w = aic_weights(wins)
    E = float(np.sum(w * np.array([x["E"] for x in wins])))
    Ej = np.sum(w[:, None] * np.array([x["Ej"] for x in wins]), axis=0)
    n = len(Ej)
    stat = float(np.sqrt((n - 1) / n * np.sum((Ej - Ej.mean()) ** 2)))
    syst = float(np.sqrt(np.sum(w * (np.array([x["E"] for x in wins]) - E) ** 2)))
    best = wins[int(np.argmax(w))]
    return {"E": E, "stat": stat, "syst": syst, "err": float(np.hypot(stat, syst)), "Ej": Ej, "tmin_onset": tfl,
            "window": [best["tmin"], best["tmax"]], "chi2dof": best["chi2"] / max(best["dof"], 1)}


def load_nucleon_matrix(qdir, role, name="N"):
    """Source-averaged smeared x smeared nucleon matrices [ncfg, t, snk, src] from *_nuc_<role>.h5."""
    rows = []
    for f in sorted(glob.glob(os.path.join(qdir, f"*_nuc_{role}.h5"))):
        with h5py.File(f, "r") as h:
            ks = sorted(k for k in h.keys() if f"{k}/N" in h)
            sites = json.loads(h.attrs["sites"])
            legacy = int(h.attrs.get("apbc_unwrapped", 0)) == 0
            mats = []
            for k in ks:
                m = h[f"{k}/{name}"][...]
                if legacy:  # pre-fix data: apply the APBC sign of three wrapped quark lines
                    m = m * site_series_signs(sites[int(k[3:])][3], m.shape[0], 48)[:, None, None]
                mats.append(m)
            if not mats:
                continue
            cid = int(h.attrs["cfg_id"])
            sc = (cid // 10000, cid % 10000)
            if sc in EXCLUDE:
                continue
            rows.append((sc, np.mean(mats, axis=0)))
    if len(rows) < 10:
        return None, None
    rows.sort(key=lambda r: r[0])
    return np.array([r[1] for r in rows]), [(r[0][0], r[0][1], 0.0) for r in rows]


def run(qdir, binsize=2, out=None, onset=True, exclude_exceptional=True, nucleon_matrix=True):
    files = sorted(glob.glob(os.path.join(qdir, "*_quark.h5")))
    EXCLUDE.clear()
    if exclude_exceptional:
        EXCLUDE.update(exceptional_configs(files))
    res = {"ncfg": len(files), "excluded": sorted(EXCLUDE), "binsize": binsize, "ainv_MeV": ainv_mev(), "light": {}, "staticlight": {},
           "gate": {}}
    ok = True
    for role, ref in UKQCD.items():
        res["light"][role] = {}
        for h, tmax in (("pi", 18), ("rho", 16), ("N", 16)):
            if h == "N" and nucleon_matrix:
                c, meta = load_nucleon_matrix(qdir, role)
                if c is None:
                    ok = False
                    continue
                pc, _ = principal_correlator(0.5 * (c + np.conj(c.swapaxes(2, 3))).real, 1, 2)
                r = energy_jk(pc, meta, binsize, 1, tmax, onset)
            else:
                c, meta = load(files, f"light/{role}/{h}")
                r = energy_jk(c, meta, binsize, 2, tmax, onset)
            if r is None:
                ok = False
                continue
            v, e = ref[h]
            pull = (r["E"] - v) / np.hypot(r["err"], e)
            res["light"][role][h] = {k: r[k] for k in ("E", "stat", "syst", "err", "window", "chi2dof", "tmin_onset")}
            res["light"][role][h].update({"ukqcd": v, "ukqcd_err": e, "pull": float(pull)})
            ok &= abs(pull) <= 2.0
    # static-light, HYP2
    mpi2, dPM, dPMj = [], [], []
    for role in UKQCD:
        E = {}
        for g in ("S_g5", "Pm_1", "Pp_g5gi"):
            C, meta = load(files, f"HYP2/staticlight/{role}/{g}")
            Cs = 0.5 * (C + np.conj(C.swapaxes(2, 3))).real
            pc, nb = principal_correlator(Cs, 1, 2)
            E[g] = energy_jk(pc, meta, binsize, 1, 10, onset)
        if not all(E.values()):
            ok = False
            continue
        d = E["Pm_1"]["Ej"] - E["S_g5"]["Ej"]
        n = len(d)
        dstat = float(np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2)))
        dE = E["Pm_1"]["E"] - E["S_g5"]["E"]
        dsys = float(np.hypot(E["Pm_1"]["syst"], E["S_g5"]["syst"]))
        deg = E["Pp_g5gi"]["E"] - E["Pm_1"]["E"]
        res["staticlight"][role] = {"aE_S": E["S_g5"]["E"], "aE_Pm": E["Pm_1"]["E"], "aE_Pm_g5gi": E["Pp_g5gi"]["E"],
                                    "a_dPmS": dE, "stat": dstat, "syst": dsys,
                                    "MeV": dE * ainv_mev(), "MeV_err": float(np.hypot(dstat, dsys)) * ainv_mev(),
                                    "heavy_spin_partner_diff_a": deg}
        if role in res["light"] and "pi" in res["light"][role]:
            mpi2.append(res["light"][role]["pi"]["E"] ** 2)
            dPM.append(dE)
            dPMj.append(np.hypot(dstat, dsys))
    if len(mpi2) >= 2:
        x, y, w = np.array(mpi2), np.array(dPM), 1 / np.array(dPMj) ** 2
        A = np.vstack([np.ones_like(x), x]).T
        cov = np.linalg.inv(A.T @ (A * w[:, None]))
        p = cov @ (A.T @ (w * y))
        chi = float(np.sum(w * (A @ p - y) ** 2))
        val, err = p[0] * ainv_mev(), np.sqrt(cov[0, 0]) * ainv_mev()
        pull = (val - BGR_PM_S[0]) / np.hypot(err, BGR_PM_S[1])
        res["gate"]["PmS_chiral_MeV"] = [float(val), float(err)]
        res["gate"]["PmS_chiral_fit_chi2"] = chi
        res["gate"]["PmS_pull_vs_BGR"] = float(pull)
        ok &= abs(pull) <= 2.0
    else:
        ok = False
    # P-wave (derivative operators) at the strange-like kappa, from the self-contained *_pw_s.h5 files
    pwf = sorted(glob.glob(os.path.join(qdir, "*_pw_s.h5")))
    if pwf:
        rows = []
        for f in pwf:
            with h5py.File(f, "r") as h:
                srcs = sorted({k.split("/")[0] for k in h.keys() if True} | set())
                ks = []
                h.visititems(lambda n, o: ks.append(n) if isinstance(o, h5py.Dataset) else None)
                srcs = sorted({k.split("/")[0] for k in ks})
                if not srcs or any(f"{s_}/PpE" not in ks for s_ in srcs):
                    continue
                sites = json.loads(h.attrs["sites"])
                legacy = int(h.attrs.get("apbc_unwrapped", 0)) == 0

                def corr(s_, c):
                    v = h[f"{s_}/{c}"][...]
                    if legacy:  # one wrapped light-quark line
                        v = v * site_series_signs(sites[int(s_[3:])][3], v.shape[0], 48)
                    return v
                avg = {c: np.mean([corr(s_, c) for s_ in srcs], axis=0) for c in ("S", "PmD", "PpE")}
                cid = int(h.attrs["cfg_id"])
                rows.append(((cid // 10000, cid % 10000), avg))
        rows.sort(key=lambda r: r[0])
        meta = [(r[0][0], r[0][1], 0.0) for r in rows]
        res["pwave_s"] = {"ncfg": len(rows)}
        if len(rows) >= 10:
            # derivative-operator correlators carry an overall minus sign (anti-Hermitian symmetric
            # derivative at the source); sign convention fixed to positive.
            sgn = {"S": 1.0, "PmD": -1.0, "PpE": -1.0}
            E = {c: energy_jk(sgn[c] * np.array([r[1][c] for r in rows]), meta, binsize, 1, 10, onset)
                 for c in ("S", "PmD", "PpE")}
            for c in ("PmD", "PpE"):
                if not (E[c] and E["S"]):
                    ok = False
                    continue
                d = E[c]["Ej"] - E["S"]["Ej"]
                n = len(d)
                dstat = float(np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2)))
                dsys = float(np.hypot(E[c]["syst"], E["S"]["syst"]))
                val = (E[c]["E"] - E["S"]["E"]) * ainv_mev()
                err = float(np.hypot(dstat, dsys)) * ainv_mev()
                ref, rerr = BGR_STATIC_STRANGE[c]
                pull = (val - ref) / np.hypot(err, rerr)
                res["pwave_s"][c] = {"MeV": float(val), "MeV_err": err, "BGR": ref, "pull": float(pull),
                                     "tmin_onset": E[c]["tmin_onset"], "window": E[c]["window"]}
                ok &= abs(pull) <= 2.0
        else:
            ok = False
    else:
        ok = False
    res["gate"]["light_hadrons_all_within_2sigma"] = all(
        abs(v["pull"]) <= 2 for r in res["light"].values() for v in r.values())
    res["gate"]["passed"] = bool(ok)
    res["gate"]["note"] = ("P- from local operators chirally extrapolated vs BGR 435; P+ (E irrep) and derivative "
                           "P- at kappa_s vs BGR static-strange 400 / 412 MeV.")
    if out:
        json.dump(res, open(out, "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    import sys
    r = run(sys.argv[1], out=sys.argv[2] if len(sys.argv) > 2 else None,
            exclude_exceptional="--no-exclusion" not in sys.argv, nucleon_matrix="--point-sink-nucleon" not in sys.argv)
    print("excluded:", r["excluded"])
    for role, d in r["light"].items():
        for h, v in d.items():
            print(f"{role} {h:3s} aM={v['E']:.4f}({v['err']*1e4:.0f}) win={v['window']} chi2/dof={v['chi2dof']:.2f}"
                  f"  UKQCD {v['ukqcd']}({v['ukqcd_err']*1e4:.0f})  pull {v['pull']:+.2f}")
    for role, v in r["staticlight"].items():
        print(f"{role} static-light: a dE(P- - S) = {v['a_dPmS']:.4f}  = {v['MeV']:.0f}({v['MeV_err']:.0f}) MeV;"
              f"  heavy-spin partner diff {v['heavy_spin_partner_diff_a']:+.4f}")
    for c, v in r.get("pwave_s", {}).items():
        if isinstance(v, dict):
            print(f"kappa_s {c} - S = {v['MeV']:.0f}({v['MeV_err']:.0f}) MeV vs BGR {v['BGR']:.0f}: pull {v['pull']:+.2f}")
    print(json.dumps(r["gate"], indent=1))
