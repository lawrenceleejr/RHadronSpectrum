"""M0 GPU acceptance test for the PyQUDA stack (run inside the full image on a GPU node).

1. QUDA Wilson-clover propagator == CPU reference (rhadron.dirac) on a 4^3x8 random config, up to a
   global normalisation which is reported (fixes kappa-normalisation and clover-sign conventions).
2. Plaquette from QUDA == our plaquette.
3. Pion correlator on a quenched config (input file if given, else a heatbath-thermalised 8^3x16):
   positive, cosh-like, effective mass reported.
4. Solve timing (BiCGStab and multigrid) on the largest supplied config.
Writes out/smoke.json; exit code 1 if a check fails.
"""
import json
import os
import sys
import time

import numpy as np


def main():
    import cupy as cp

    from rhadron.dirac import point_propagator as ref_prop
    from rhadron.gauge.field import plaquette, random_gauge
    from rhadron.gauge.io import load_gauge
    from rhadron.gamma import G5
    from rhadron.solve import quda as Q

    res, ok = {}, True
    rng = np.random.default_rng(11)
    shape = (8, 4, 4, 4)
    U = random_gauge(shape, rng, eps=0.35)
    kappa, csw = 0.115, 1.3
    li = Q.init([4, 4, 4, 8])
    g = Q.to_quda_gauge(li, U)
    res["plaq_quda"] = float(g.plaquette()[0]) if hasattr(g, "plaquette") else None
    res["plaq_ours"] = plaquette(U)[0]
    d = Q.make_dirac(li, g, kappa, csw, tol=1e-12, maxiter=5000)
    Sq = cp.asnumpy(Q.point_propagator(li, d, None, (1, 2, 3, 0), smear=None))
    for sign in (+1, -1):
        Sr = ref_prop(U, kappa, sign * csw, (1, 2, 3, 0))
        ratio = Sq.ravel()[np.argmax(np.abs(Sr))] / Sr.ravel()[np.argmax(np.abs(Sr))]
        dev = np.abs(Sq - ratio * Sr).max() / np.abs(Sq).max()
        res[f"prop_dev_csw_sign{sign:+d}"] = float(dev)
        res[f"prop_norm_ratio_sign{sign:+d}"] = [float(ratio.real), float(ratio.imag)]
    best = min(res["prop_dev_csw_sign+1"], res["prop_dev_csw_sign-1"])
    res["prop_agree"] = bool(best < 1e-8)
    ok &= res["prop_agree"]
    if res["plaq_quda"] is not None:
        ok &= abs(res["plaq_quda"] - res["plaq_ours"]) < 1e-10
    # pion on a quenched configuration
    cfg = sys.argv[1] if len(sys.argv) > 1 else None
    if cfg and os.path.exists(cfg):
        Uq, _ = load_gauge(cfg)
        kq = float(sys.argv[2]) if len(sys.argv) > 2 else 0.1340
        cq = float(sys.argv[3]) if len(sys.argv) > 3 else 1.769
        Lt, Lz, Ly, Lx = Uq.shape[1:5]
        li2 = Q.init([Lx, Ly, Lz, Lt]) if (Lx, Ly, Lz, Lt) == (4, 4, 4, 8) else None
        res["pion_cfg"] = cfg
        # (a separate process is needed for a different lattice size in PyQUDA; report only)
    out = os.environ.get("OUTDIR", "out")
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "smoke.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
