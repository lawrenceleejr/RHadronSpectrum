"""Quark-sector analysis: light hadrons (M3), fundamental static-light splittings (M3),
R-mesons / R-baryons (M4, blinded relative to the gluelumps)."""
import glob
import json
import os

import h5py
import numpy as np

from . import blind
from .gluelump import aic_weights, binned, fit_windows, principal_correlator


def load(files, prefix):
    rows = []
    for f in files:
        with h5py.File(f, "r") as h:
            rows.append((int(h.attrs["stream"]), int(h.attrs["cfg"]), f))
    rows.sort()
    data, meta = {}, []
    for s, c, f in rows:
        with h5py.File(f, "r") as h:
            def visit(name, obj):
                if isinstance(obj, h5py.Dataset) and name.startswith(prefix):
                    data.setdefault(name, []).append(obj[...])
            h.visititems(visit)
            meta.append((s, c, float(h.attrs["plaq"])))
    return {k: np.array(v) for k, v in data.items()}, meta


def energy(pc, t0, tmax=None):
    """AIC-averaged ground-state energy with jackknife samples from per-sample correlators."""
    T = pc.shape[1] - 1 if tmax is None else tmax
    wins = fit_windows(pc.real, t0, T)
    if not wins:
        return None
    w = aic_weights(wins)
    E = float(np.sum(w * np.array([x["E"] for x in wins])))
    Ej = np.sum(w[:, None] * np.array([x["Ej"] for x in wins]), axis=0)
    n = len(Ej)
    stat = float(np.sqrt((n - 1) / n * np.sum((Ej - Ej.mean()) ** 2)))
    syst = float(np.sqrt(np.sum(w * (np.array([x["E"] for x in wins]) - E) ** 2)))
    best = wins[int(np.argmax(w))]
    return {"aE": E, "stat": stat, "syst": syst, "Ej": Ej, "window": [best["tmin"], best["tmax"]],
            "chi2dof": best["chi2"] / max(best["dof"], 1)}


def light_hadrons(files, binsize=1, tmax=None):
    data, meta = load(files, "light/")
    out = {}
    for k, v in data.items():
        c = binned(v.real, meta, binsize)
        if k.endswith("/N"):
            c = c  # forward nucleon (P+), t < Lt/2
        Lt = c.shape[1]
        r = energy(c, 0, tmax or Lt // 2 - 2)
        if r:
            r.pop("Ej")
            out[k] = r
    return out


def matrix_channels(files, prefix, binsize=1, t0=1, td=2):
    """Per channel: principal correlator of the (snk level, src level) matrix -> energies (jk kept)."""
    data, meta = load(files, prefix)
    res = {}
    for k, C in data.items():
        Cs = 0.5 * (C + np.conj(C.swapaxes(2, 3))).real
        try:
            pc, nb = principal_correlator(Cs, t0, td)
        except Exception:  # noqa: BLE001
            continue
        r = energy(binned(pc, meta, binsize), t0)
        if r:
            res[k] = r
    return res


def splittings(levels, ref):
    """Correlated differences E_k - E_ref from jackknife samples (same binned configs)."""
    out = {}
    for k, r in levels.items():
        if ref not in levels:
            break
        d = r["Ej"] - levels[ref]["Ej"]
        n = len(d)
        out[k] = {"a_dE": r["aE"] - levels[ref]["aE"],
                  "stat": float(np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2))),
                  "syst": float(np.hypot(r["syst"], levels[ref]["syst"]))}
    return out


def blinded(levels, tag):
    off = blind.offset(tag)
    return {k: {**v, "aE": v["aE"] + off, "Ej": v["Ej"] + off} for k, v in levels.items()}
