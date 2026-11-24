"""M4: quenched R-mesons and R-baryons, blinded relative to the gluelumps.

Energies: GEVP (2 smearing levels) principal correlators, plateau-onset rule + AIC (as in M3),
exceptional configurations excluded, bin size 2 within streams.  Splittings to the 1+- gluelump use the
SAME configurations (matched by (stream, cfg)), so jackknife differences are correlated.
Blinding: every R-hadron energy is shifted by blind.offset(tag) until `unblind=True` (called once,
logged).  Differences among R-hadrons are unaffected; R-hadron - gluelump is hidden.
Symmetry checks on production data: Hermiticity of C_ij(t), Im C consistent with 0, HYP1 vs HYP2
splittings (static-action independence).
"""
import glob
import json
import os

import h5py
import numpy as np

from . import blind
from .gluelump import binned, principal_correlator
from .m3 import energy_jk, exceptional_configs

BIN = 2


def _key(h):
    return int(h.attrs["stream"]), int(h.attrs["cfg"])


def load_quark(files, exclude):
    """{dataset name: {(stream, cfg): array}} for every rmeson/rbaryon dataset."""
    out = {}
    for f in files:
        with h5py.File(f, "r") as h:
            k = _key(h)
            if k in exclude:
                continue
            names = []
            h.visititems(lambda n, o: names.append(n) if isinstance(o, h5py.Dataset) and ("/rmeson/" in n or "/rbaryon/" in n) else None)
            for n in names:
                out.setdefault(n, {})[k] = h[n][...]
    return out


def load_glue(tag, keys, action="HYP2", channel="T1g-"):
    out = {}
    for s, c in keys:
        f = f"/scratch/llee/rhadron/data/{tag}/s{s}/out/{tag}_s{s}_c{c:04d}_glue.h5"
        if os.path.exists(f):
            with h5py.File(f, "r") as h:
                if action in h and channel in h[action]:
                    out[(s, c)] = h[f"{action}/{channel}"][...]
    return out


def channel_energy(byk, keys, t0=1, td=2, tmax=None):
    C = np.array([byk[k] for k in keys])
    meta = [(k[0], k[1], 0.0) for k in keys]
    Cs = 0.5 * (C + np.conj(C.swapaxes(2, 3))).real
    pc, nb = principal_correlator(Cs, t0, td)
    T = pc.shape[1] - 1 if tmax is None else tmax
    return energy_jk(pc, meta, BIN, t0, T, True)


def symmetry_checks(byk, keys):
    C = np.array([byk[k] for k in keys])
    n = len(C)
    herm = C - np.conj(C.swapaxes(2, 3))
    hz = np.abs(herm.mean(0)) / (np.abs(herm).std(0) / np.sqrt(n) + 1e-300)
    im = np.abs(C.imag.mean(0)) / (C.imag.std(0) / np.sqrt(n) + 1e-300)
    return {"hermiticity_max_sigma": float(np.nanmax(hz[1:8])), "imag_max_sigma": float(np.nanmax(im[1:8]))}


def run(tag, qdir, out=None, unblind=False):
    files = sorted(glob.glob(os.path.join(qdir, "*_quark.h5")))
    excl = exceptional_configs(files)
    data = load_quark(files, excl)
    keys_all = sorted(set.intersection(*[set(v) for v in data.values()]))
    glue = {a: load_glue(tag, keys_all, a) for a in ("HYP2", "HYP1")}
    off = 0.0 if unblind else blind.offset(tag)
    res = {"tag": tag, "ncfg": len(keys_all), "excluded": sorted(excl), "blinded": not unblind, "channels": {},
           "symmetry": {}}
    ref = {}
    for act in ("HYP2", "HYP1"):
        keys = sorted(k for k in keys_all if k in glue[act])
        if len(keys) < 10:
            continue
        g = channel_energy(glue[act], keys)
        ref[act] = (keys, g)
        res["channels"][f"{act}/gluelump/T1g-"] = {"aE": g["E"], "err": g["err"], "window": g["window"], "n": len(keys)}
    for name, byk in sorted(data.items()):
        act = name.split("/")[0]
        if act not in ref:
            continue
        keys, g = ref[act]
        keys = [k for k in keys if k in byk]
        if len(keys) != len(ref[act][0]):
            continue
        r = channel_energy(byk, keys)
        if r is None:
            res["channels"][name] = {"ok": False}
            continue
        d = (r["Ej"] + off) - g["Ej"]
        n = len(d)
        stat = float(np.sqrt((n - 1) / n * np.sum((d - d.mean()) ** 2)))
        res["channels"][name] = {"ok": True, "aE_blinded": r["E"] + off, "err": r["err"], "window": r["window"],
                                 "a_dE_vs_gluelump_blinded": float(r["E"] + off - g["E"]),
                                 "dE_stat": stat, "dE_syst": float(np.hypot(r["syst"], g["syst"]))}
        res["symmetry"][name] = symmetry_checks(byk, keys)
    if out:
        json.dump(res, open(out, "w"), indent=1, default=float)
    return res


if __name__ == "__main__":
    import sys
    tag, qdir = sys.argv[1], sys.argv[2]
    r = run(tag, qdir, out=sys.argv[3] if len(sys.argv) > 3 else None, unblind="--UNBLIND" in sys.argv)
    print("ncfg", r["ncfg"], "blinded", r["blinded"])
    for k, v in r["channels"].items():
        if v.get("ok", True) and "aE_blinded" in v:
            print(f"{k:55s} aE*={v['aE_blinded']:.4f}({v['err']*1e4:.0f}) dE*={v['a_dE_vs_gluelump_blinded']:+.4f} win={v['window']}")
