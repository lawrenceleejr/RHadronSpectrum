"""Gluelump spectrum analysis for one ensemble.

Reads every *_glue.h5 of the ensemble, bins in configuration order per stream (streams = replicas),
and per channel (irrep, C):
  * basis pruning: operators normalised by C_ii(t0); keep principal components of C(t0) with
    eigenvalue > eps * max (removes near-linearly-dependent operators)
  * GEVP at (t0, td) on the mean -> fixed eigenvectors -> projected ground-state correlator per sample
  * correlated single-exponential fits over all windows [tmin, tmax] with tmin >= t0+1; AIC average
  * splittings dE = E(channel) - E(T1g-) from the same jackknife samples (correlated)
Continuum labels (lowest J for each O_h irrep): A1->0, T1->1, E/T2->2, A2->3; g/u -> P = +/-.
"""
import glob
import json
import os

import h5py
import numpy as np

from .fits import fit_corr
from .gevp import gevp
from .resample import bin_data, jackknife_samples

JLOW = {"A1": "0", "T1": "1", "E": "2", "T2": "2", "A2": "3"}


def jpc(key):
    ir, cl = key[:-1], key[-1]
    base, par = ir[:-1], ir[-1]
    return f"{JLOW[base]}{'+' if par == 'g' else '-'}{cl}"


def load(files, action="HYP2"):
    """Returns ({channel: array[ncfg, T, n, n]}, meta list) ordered by (stream, cfg)."""
    rows = []
    for f in files:
        with h5py.File(f, "r") as h:
            if action not in h:
                continue
            rows.append((int(h.attrs["stream"]), int(h.attrs["cfg"]), f))
    rows.sort()
    data, meta = {}, []
    for s, c, f in rows:
        with h5py.File(f, "r") as h:
            g = h[action]
            for k in g:
                data.setdefault(k, []).append(g[k][...])
            meta.append((s, c, float(h.attrs["plaq"])))
    return {k: np.array(v) for k, v in data.items()}, meta


def binned(x, meta, b):
    """Bin within streams (never across), then concatenate."""
    streams = np.array([m[0] for m in meta])
    out = []
    for s in np.unique(streams):
        xs = x[streams == s]
        if len(xs) >= b:
            out.append(bin_data(xs, b))
    return np.concatenate(out)


def prune(Cmean, t0, eps):
    d = np.sqrt(np.abs(np.diagonal(Cmean[t0])))
    N = Cmean / d[None, :, None] / d[None, None, :]
    w, v = np.linalg.eigh(N[t0])
    keep = v[:, w > eps * w.max()]
    return keep / d[:, None]  # columns: operator combinations in the original basis


def principal_correlator(C, t0, td, eps=1e-3):
    """C[ncfg, T, n, n] -> projected ground-state correlator per config [ncfg, T] (GEVP on mean)."""
    Cs = 0.5 * (C + C.swapaxes(2, 3))
    Cm = Cs.mean(axis=0)
    P = prune(Cm, t0, eps)
    Cp = np.einsum("ia,ctij,jb->ctab", P, Cs, P)
    lam, v = gevp(Cp.mean(axis=0), t0, td)
    v0 = v[:, 0]
    return np.einsum("i,ctij,j->ct", v0, Cp, v0), P.shape[1]


def plateau_onset(samples, t_first, tmax_avail):
    """Pre-registered rule (logbook 2026-11-22): first t >= t_first with |m(t) - m(t+2)| < sigma for
    two consecutive t, using jackknife effective masses.  Returns t_first if never satisfied."""
    jk = jackknife_samples(samples)
    n = len(jk)
    with np.errstate(divide="ignore", invalid="ignore"):
        me = np.log(jk[:, :-1] / jk[:, 1:])
    m = me.mean(axis=0)
    ok = []
    for t in range(t_first, min(tmax_avail - 2, me.shape[1] - 2)):
        d = me[:, t] - me[:, t + 2]
        sig = np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2))
        ok.append((t, bool(np.isfinite(sig) and abs(m[t] - m[t + 2]) < sig)))
    for (t, a), (_, b) in zip(ok, ok[1:]):
        if a and b:
            return t
    return t_first


def fit_windows(samples, t0, tmax_avail, min_len=3, tmin_floor=None):
    """Correlated single-exp fits over windows; returns list of window results with jackknife E."""
    n = len(samples)
    jk = jackknife_samples(samples)
    mean = samples.mean(axis=0)
    cov = np.cov(samples, rowvar=False) / n
    out = []
    start = t0 + 1 if tmin_floor is None else max(t0 + 1, tmin_floor)
    for tmin in range(start, tmax_avail - min_len + 2):
        for tmax in range(tmin + min_len - 1, tmax_avail + 1):
            t = np.arange(tmin, tmax + 1)
            if np.any(mean[t] <= 0):
                continue
            # signal-to-noise cut: stop windows once the correlator is consistent with zero
            if np.any(mean[t] < 2 * np.sqrt(np.diag(cov)[t])):
                continue
            try:
                p, chi2, dof = fit_corr(mean, cov, t, 1)
                Ej = np.array([fit_corr(j, cov, t, 1, p0=p)[0][1] for j in jk])
            except Exception:  # noqa: BLE001
                continue
            if not np.isfinite(p[1]) or p[1] <= 0:
                continue
            out.append({"tmin": tmin, "tmax": tmax, "E": p[1], "Ej": Ej, "chi2": chi2, "dof": dof,
                        "k": 2, "n": len(t)})
    return out


def aic_weights(wins):
    a = np.array([w["chi2"] + 2 * w["k"] - 2 * w["n"] for w in wins])
    w = np.exp(-0.5 * (a - a.min()))
    return w / w.sum()


def analyse(files, action="HYP2", binsize=1, t0=1, td=2, eps=1e-3, ref="T1g-"):
    data, meta = load(files, action)
    res = {"ncfg": len(meta), "action": action, "binsize": binsize, "t0": t0, "td": td, "channels": {}}
    proj = {}
    for k, C in data.items():
        pc, nb = principal_correlator(C, t0, td, eps)
        proj[k] = (binned(pc, meta, binsize), nb)
    nb_samples = len(next(iter(proj.values()))[0])
    # per-channel AIC-averaged energy, keeping jackknife distributions for correlated differences
    Ejk = {}
    for k, (pc, nb) in proj.items():
        T = pc.shape[1] - 1
        wins = fit_windows(pc, t0, T)
        if not wins:
            res["channels"][k] = {"jpc": jpc(k), "basis": nb, "ok": False}
            continue
        w = aic_weights(wins)
        E = np.sum(w * np.array([x["E"] for x in wins]))
        Ej = np.sum(w[:, None] * np.array([x["Ej"] for x in wins]), axis=0)
        n = len(Ej)
        stat = np.sqrt((n - 1) / n * np.sum((Ej - Ej.mean()) ** 2))
        syst = np.sqrt(np.sum(w * (np.array([x["E"] for x in wins]) - E) ** 2))
        best = wins[int(np.argmax(w))]
        Ejk[k] = Ej
        res["channels"][k] = {"jpc": jpc(k), "basis": nb, "ok": True, "aE": E, "aE_stat": stat,
                              "aE_syst": syst, "best_window": [best["tmin"], best["tmax"]],
                              "best_chi2dof": best["chi2"] / max(best["dof"], 1), "nwin": len(wins)}
    if ref in Ejk:
        for k, Ej in Ejk.items():
            d = Ej - Ejk[ref]
            n = len(d)
            c = res["channels"][k]
            c["a_dE"] = c["aE"] - res["channels"][ref]["aE"]
            c["a_dE_stat"] = float(np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2)))
            c["a_dE_syst"] = float(np.hypot(c["aE_syst"], res["channels"][ref]["aE_syst"]))
    res["nsamples"] = nb_samples
    return res


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("datadir")
    p.add_argument("--tag", required=True)
    p.add_argument("--action", default="HYP2")
    p.add_argument("--bin", type=int, default=1)
    p.add_argument("--t0", type=int, default=1)
    p.add_argument("--td", type=int, default=2)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    files = sorted(glob.glob(os.path.join(a.datadir, "s*", "out", f"{a.tag}_s*_c*_glue.h5")))
    res = analyse(files, a.action, a.bin, a.t0, a.td)
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print(json.dumps({k: (v.get("jpc"), v.get("a_dE"), v.get("a_dE_stat")) for k, v in res["channels"].items()}, indent=0))


if __name__ == "__main__":
    main()
