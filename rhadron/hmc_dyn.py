"""N_f = 2+1 clover HMC with PyQUDA (Stage B self-generation at PACS-CS parameters).

Iwasaki gauge action + 2-flavour clover (u, d) + 1-flavour RHMC clover (s).  Nested Omelyan
integrator: fermion forces on the outer level, gauge force on the inner level.  Eviction safe: the
gauge field is checkpointed after every trajectory (our HDF5 format, double precision) with the
trajectory count and RNG-relevant metadata; a trajectory log (JSON lines) records dH, acceptance,
plaquette, timing.  Configurations are saved every `save_every` trajectories after thermalisation.
"""
import json
import os
import time
from math import exp

import numpy as np

from .gauge import io


def run(ens, outdir, until, start=None, log=print):
    from pyquda.action import CloverWilsonAction, GaugeAction
    from pyquda.enum_quda import QudaVerbosity
    from pyquda.field import evenodd
    from pyquda.hmc import HMC, O4Nf5Ng0V
    from pyquda_utils import core
    from pyquda_utils.hmc_param import fermionRationalParam, iwasakiGaugeLoopParam

    Lt, Lz, Ly, Lx = ens["shape"]
    tag = ens["tag"]
    h = ens["hmc"]
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "quda_tune"), exist_ok=True)
    core.init([1, 1, 1, 1], resource_path=os.path.join(outdir, "quda_tune"))
    li = core.LatticeInfo([Lx, Ly, Lz, Lt], t_boundary=-1, anisotropy=1.0)
    m = lambda k: 1.0 / (2.0 * k) - 4.0  # noqa: E731
    tol, maxiter, csw = float(h.get("tol", 1e-9)), int(h.get("maxiter", 5000)), float(ens["csw"])
    rp = h["rational"]  # [order_md, order_action, ...] passed through to fermionRationalParam
    monomials = [
        GaugeAction(li, iwasakiGaugeLoopParam(), float(ens["beta"])),
        CloverWilsonAction(li, fermionRationalParam(2, *rp), m(float(ens["kappa_ud"])), 2, tol, maxiter, csw),
        CloverWilsonAction(li, fermionRationalParam(1, *rp), m(float(ens["kappa_s"])), 1, tol, maxiter, csw),
    ]
    # Avoid QUDA's half-precision clover path in the multishift (RHMC) force: it aborts with
    # "max_element(0) appears unset" (clover_field_order.h) for this build.  Double/single only.
    from pyquda.enum_quda import QudaPrecision as QP
    for mono in monomials[1:]:
        mono.dirac.setPrecision(cuda=QP.QUDA_DOUBLE_PRECISION, sloppy=QP.QUDA_SINGLE_PRECISION,
                                refinement_sloppy=QP.QUDA_SINGLE_PRECISION,
                                precondition=QP.QUDA_SINGLE_PRECISION)
    hmc_inner = HMC(li, monomials[:1], O4Nf5Ng0V(int(h["n_inner"])))
    hmc = HMC(li, monomials[1:], O4Nf5Ng0V(int(h["n_outer"])), hmc_inner)
    hmc.setFermionVerbosity(QudaVerbosity.QUDA_SILENT)

    ck = os.path.join(outdir, f"{tag}_s{ens.get('stream', 0)}_ckpt.h5")
    traj = 0
    if os.path.exists(ck) or (start and os.path.exists(start)):
        U, at = io.load_gauge(ck if os.path.exists(ck) else start)
        traj = int(at["traj"])
        gauge = core.LatticeGauge(li, evenodd(U, [1, 2, 3, 4]))
        log(f"resume at trajectory {traj}", flush=True)
    else:
        gauge = core.LatticeGauge(li)  # cold start
    hmc.initialize(int(ens.get("seed", 1)) * 100003 + 1009 * int(ens.get("stream", 0)) + traj, gauge)
    tau = float(h.get("tau", 1.0))
    meta = {"ensemble": tag, "beta": ens["beta"], "kappa_ud": ens["kappa_ud"], "kappa_s": ens["kappa_s"],
            "csw": csw, "ens_hash": io.config_hash(ens), "git_sha": io.git_sha()}
    logf = open(os.path.join(outdir, f"{tag}_s{ens.get('stream', 0)}_hmc_log_from{traj:05d}.jsonl"), "a")  # one file per segment
    while traj < until:
        t0 = time.perf_counter()
        hmc.gaussMom()
        hmc.samplePhi()
        k0, p0 = hmc.momAction(), hmc.gaugeAction() + hmc.fermionAction()
        hmc.integrate(tau, 2e-15)
        k1, p1 = hmc.momAction(), hmc.gaugeAction() + hmc.fermionAction()
        dH = (k1 + p1) - (k0 + p0)
        warm = traj < int(h.get("n_warm_noreject", 0))
        acc = hmc.accept(dH)
        if acc or warm:
            hmc.saveGauge(gauge)
        else:
            hmc.loadGauge(gauge)
        traj += 1
        plaq = float(hmc.plaquette()[0])
        rec = {"traj": traj, "dH": float(dH), "accept": bool(acc), "warm": warm, "plaq": plaq,
               "exp_mdH": float(exp(min(-dH, 50))), "sec": time.perf_counter() - t0}
        logf.write(json.dumps(rec) + "\n")
        logf.flush()
        log(json.dumps(rec), flush=True)
        U = gauge.lexico()
        io.save_gauge(ck, U, {**meta, "traj": traj}, precision="double")
        if traj > int(h["n_therm"]) and (traj - int(h["n_therm"])) % int(h["save_every"]) == 0:
            cfg = (traj - int(h["n_therm"])) // int(h["save_every"])
            io.save_gauge(os.path.join(outdir, f"{tag}_s{ens.get('stream', 0)}_c{cfg:04d}.h5"), U,
                          {**meta, "traj": traj, "cfg": cfg, "stream": ens.get("stream", 0), "plaq": plaq,
                           "sweeps": traj}, precision="single")
    logf.close()
