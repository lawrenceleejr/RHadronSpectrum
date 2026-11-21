"""Command-line entry points (job payloads).  `python -m rhadron.cli <cmd> ...`

gen   quenched heatbath/OR stream segment with fused gluelump measurement (eviction-safe: resumes
      from the newest checkpoint in the working directory; every output written atomically).
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import yaml

from .backend import cp, to_numpy
from .gauge import io
from .gauge.field import plaquette, random_gauge, unit_gauge
from .gauge.quenched import sweep
from .gauge.smear import ape_spatial
from .operators.gluelump import measure
from .static import static_links


def _xp(use_gpu):
    if use_gpu and cp is not None:
        try:
            cp.cuda.runtime.getDeviceCount()
            return cp
        except Exception:  # noqa: BLE001
            pass
    return np


def _rng(xp, seed):
    return xp.random.default_rng(seed)


def gluelump_measure(U, gcfg, xp, with_hyp1):
    V_levels = [ape_spatial(U, gcfg["ape_alpha"], n) for n in gcfg["ape_levels"]]
    acts = {"HYP2": static_links(U, "HYP2")}
    if with_hyp1:
        acts["HYP1"] = static_links(U, "HYP1")
    res, labels = measure(V_levels, acts, gcfg["tmax"], shapes=gcfg["shapes"])
    out = {}
    for act, d in res.items():
        for (ir, cl), c in d.items():
            out[f"{act}/{ir}{cl}"] = to_numpy(c)
    lab = {f"{ir}{cl}": [list(map(str, x)) for x in v] for (ir, cl), v in labels.items()}
    return out, lab


def cmd_gen(a):
    ens = yaml.safe_load(open(a.ensemble))
    xp = _xp(not a.cpu)
    shape = tuple(ens["shape"])  # (Lt, Lz, Ly, Lx)
    tag, stream = ens["tag"], a.stream
    beta, n_or = float(ens["beta"]), int(ens.get("n_or", 4))
    nsep, ntherm = int(ens["n_sep"]), int(ens["n_therm"])
    os.makedirs(a.outdir, exist_ok=True)
    ck = os.path.join(a.outdir, f"{tag}_s{stream}_ckpt.h5")
    if os.path.exists(ck):
        U, at = io.load_gauge(ck)
        done = int(at["sweeps"])
        print(f"resume from {ck} at sweep {done}", flush=True)
    elif a.start and os.path.exists(a.start):
        U, at = io.load_gauge(a.start)
        done = int(at["sweeps"])
        print(f"start from {a.start} at sweep {done}", flush=True)
    else:
        U = unit_gauge(shape) if stream % 2 == 0 else random_gauge(shape, np.random.default_rng(1000 + stream))
        done = 0
    U = xp.asarray(U)
    rng = _rng(xp, int(ens.get("seed", 1)) * 1000003 + stream * 10007 + done)
    target = a.until
    meta = {"ensemble": tag, "stream": stream, "beta": beta, "n_or": n_or,
            "ens_hash": io.config_hash(ens), "git_sha": io.git_sha()}
    t_start = time.time()
    while done < target:
        sweep(U, beta, rng, n_or=n_or)
        done += 1
        if done % 10 == 0:
            print(f"sweep {done} plaq {plaquette(U)[0]:.6f} {time.time() - t_start:.0f}s", flush=True)
        if done >= ntherm and (done - ntherm) % nsep == 0:
            cfg_id = (done - ntherm) // nsep
            name = f"{tag}_s{stream}_c{cfg_id:04d}"
            Un = to_numpy(U)
            p = plaquette(U)
            if "gluelump" in ens and not a.no_measure:
                hyp1 = cfg_id % int(ens["gluelump"].get("hyp1_every", 4)) == 0
                t0 = time.time()
                corr, lab = gluelump_measure(U, ens["gluelump"], xp, hyp1)
                io.save_h5(os.path.join(a.outdir, f"{name}_glue.h5"), corr,
                           {**meta, "cfg": cfg_id, "sweeps": done, "plaq": p[0],
                            "labels": json.dumps(lab), "glue_params": ens["gluelump"]})
                print(f"measured {name} in {time.time() - t0:.0f}s", flush=True)
            if ens.get("save_configs", True):
                io.save_gauge(os.path.join(a.outdir, f"{name}.h5"), Un,
                              {**meta, "cfg": cfg_id, "sweeps": done, "plaq": p[0]}, precision="single")
            io.save_gauge(ck, Un, {**meta, "sweeps": done}, precision="double")
    io.save_gauge(ck, to_numpy(U), {**meta, "sweeps": done}, precision="double")
    print(f"done: sweep {done}, {time.time() - t_start:.0f}s", flush=True)


def cmd_bench(a):
    """Time compound sweeps and one gluelump measurement for each ensemble YAML (GPU if present)."""
    xp = _xp(not a.cpu)
    out = {}
    for path in a.ensembles:
        ens = yaml.safe_load(open(path))
        shape = tuple(ens["shape"])
        U = xp.asarray(random_gauge(shape, np.random.default_rng(0), eps=0.3))
        rng = _rng(xp, 1)
        sweep(U, float(ens["beta"]), rng, n_or=int(ens.get("n_or", 4)))  # warm-up / JIT
        if xp is not np:
            cp.cuda.Device().synchronize()
        t0 = time.time()
        for _ in range(a.sweeps):
            sweep(U, float(ens["beta"]), rng, n_or=int(ens.get("n_or", 4)))
        if xp is not np:
            cp.cuda.Device().synchronize()
        ts = (time.time() - t0) / a.sweeps
        t0 = time.time()
        gluelump_measure(U, ens["gluelump"], xp, True)
        if xp is not np:
            cp.cuda.Device().synchronize()
        tm = time.time() - t0
        mem = cp.get_default_memory_pool().total_bytes() / 2**30 if xp is not np else 0
        out[ens["tag"]] = {"sec_per_sweep": ts, "sec_per_measure_hyp2_hyp1": tm, "pool_GB": mem}
        print(ens["tag"], out[ens["tag"]], flush=True)
    os.makedirs(a.outdir, exist_ok=True)
    json.dump(out, open(os.path.join(a.outdir, "bench.json"), "w"), indent=1)


def main(argv=None):
    p = argparse.ArgumentParser(prog="rhadron")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--ensemble", required=True)
    g.add_argument("--stream", type=int, required=True)
    g.add_argument("--until", type=int, required=True, help="absolute compound-sweep count to reach")
    g.add_argument("--start", default=None, help="checkpoint to continue from")
    g.add_argument("--outdir", default=".")
    g.add_argument("--cpu", action="store_true")
    g.add_argument("--no-measure", action="store_true")
    b = sub.add_parser("bench")
    b.add_argument("ensembles", nargs="+")
    b.add_argument("--sweeps", type=int, default=3)
    b.add_argument("--outdir", default="out")
    b.add_argument("--cpu", action="store_true")
    a = p.parse_args(argv)
    {"gen": cmd_gen, "bench": cmd_bench}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
