"""Light-quark propagators with QUDA (via PyQUDA), Wilson-clover, optional adaptive multigrid.

Layout conversion: our gauge field is lexicographic U[mu, t, z, y, x, a, b]; PyQUDA stores even-odd
fields [.., 2, Lt, Lz, Ly, Lx/2, ...].  Propagators are returned as lexicographic
S[t, z, y, x, s, a, s0, a0] (spin, colour at the sink; spin0, colour0 at the source), DeGrand-Rossi
basis, kappa normalisation of rhadron.dirac (normalisation calibrated in tests/gpu).
"""
import numpy as np

from ..backend import get_xp
from ..dirac import wuppertal

_INIT = {}


def init(latt_size_xyzt, resource_path=""):
    """Initialise PyQUDA once per process for a lattice [Lx, Ly, Lz, Lt]."""
    import pyquda

    key = tuple(latt_size_xyzt)
    if not _INIT:
        pyquda.init([1, 1, 1, 1], list(latt_size_xyzt), backend="cupy", resource_path=resource_path,
                    enable_mps=False)
        _INIT["done"] = key
    from pyquda.field import LatticeInfo
    return LatticeInfo(list(latt_size_xyzt), t_boundary=-1, anisotropy=1.0)


def to_quda_gauge(latt_info, U):
    from pyquda.field import LatticeGauge, evenodd

    Un = np.asarray(U.get() if hasattr(U, "get") else U)
    return LatticeGauge(latt_info, evenodd(Un, [1, 2, 3, 4]))


def make_dirac(latt_info, gauge, kappa, csw, tol=1e-10, maxiter=2000, multigrid=None):
    """multigrid: None (BiCGStab) or list of block sizes per level, e.g. [[4,4,4,4],[2,2,2,2]]."""
    from pyquda.dirac import CloverWilsonDirac

    mass = 1.0 / (2.0 * kappa) - 4.0
    d = CloverWilsonDirac(latt_info, mass, tol, maxiter, clover_csw=csw, multigrid=multigrid)
    d.loadGauge(gauge)
    return d


def _fermion_from_lexico(latt_info, psi):
    """psi[t,z,y,x,s,a] (cupy/numpy, lexico) -> pyquda LatticeFermion."""
    from pyquda.field import LatticeFermion

    xp = get_xp(psi)
    eo = evenodd_xp(psi, xp)
    f = LatticeFermion(latt_info)
    f.data[...] = eo
    return f


def evenodd_xp(a, xp):
    """Lexico [t,z,y,x,...] -> even-odd [2, t, z, y, x/2, ...] on numpy or cupy."""
    Lt, Lz, Ly, Lx = a.shape[:4]
    t, z, y = np.indices((Lt, Lz, Ly))
    par = xp.asarray(((t + z + y) % 2)[..., None])
    a0, a1 = a[..., 0::2, :, :], a[..., 1::2, :, :]  # x even / odd
    sel = par.reshape(Lt, Lz, Ly, 1, *([1] * (a.ndim - 4)))
    even = xp.where(sel == 0, a0, a1)
    odd = xp.where(sel == 0, a1, a0)
    return xp.stack([even, odd])


def lexico_xp(e, xp):
    """Inverse of evenodd_xp."""
    even, odd = e[0], e[1]
    Lt, Lz, Ly, Lxh = even.shape[:4]
    t, z, y = np.indices((Lt, Lz, Ly))
    sel = xp.asarray(((t + z + y) % 2)).reshape(Lt, Lz, Ly, 1, *([1] * (even.ndim - 4)))
    xeven = xp.where(sel == 0, even, odd)
    xodd = xp.where(sel == 0, odd, even)
    out = xp.empty((Lt, Lz, Ly, 2 * Lxh) + even.shape[4:], dtype=even.dtype)
    out[:, :, :, 0::2] = xeven
    out[:, :, :, 1::2] = xodd
    return out


def point_propagator(latt_info, dirac, U_smear, x0, smear=None, sink_sites_only=None):
    """Smeared-source/smeared-sink propagator from x0 = (x, y, z, t).
    U_smear: (cupy) link field used for Wuppertal smearing; smear = (alpha, n) or None.
    Returns full lexico S[t,z,y,x,s,a,s0,a0] (cupy)."""
    import cupy as cp

    Lx, Ly, Lz, Lt = latt_info.global_size if hasattr(latt_info, "global_size") else latt_info.size
    S = cp.zeros((Lt, Lz, Ly, Lx, 4, 3, 4, 3), dtype=cp.complex128)
    for s0 in range(4):
        for a0 in range(3):
            b = cp.zeros((Lt, Lz, Ly, Lx, 4, 3), dtype=cp.complex128)
            b[x0[3], x0[2], x0[1], x0[0], s0, a0] = 1.0
            if smear:
                b = wuppertal(U_smear, b, smear[0], smear[1])
            x = dirac.invert(_fermion_from_lexico(latt_info, b))
            psi = lexico_xp(cp.asarray(x.data), cp)
            if smear:
                psi = wuppertal(U_smear, psi, smear[0], smear[1])
            S[..., s0, a0] = psi
    return S
