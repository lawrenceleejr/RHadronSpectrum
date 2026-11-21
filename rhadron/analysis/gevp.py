"""Generalised eigenvalue problem C(t) v = lambda(t, t0) C(t0) v, with eigenvector tracking."""
import numpy as np
import scipy.linalg as sla


def gevp(C, t0, td=None):
    """C[t, i, j] real symmetric.  Returns lambda[t, n] (sorted descending at t = td, then fixed
    eigenvectors from td: 'fixed-vector' method) and the eigenvectors v[:, n] at td.
    td=None: solve at every t and sort by eigenvalue (per-t method)."""
    C = 0.5 * (C + C.swapaxes(1, 2)).real
    nT, N = C.shape[:2]
    if td is not None:
        w, v = sla.eigh(C[td], C[t0])
        order = np.argsort(w)[::-1]
        v = v[:, order]
        lam = np.einsum("in,tij,jn->tn", v, C, v) / np.einsum("in,ij,jn->n", v, C[t0], v)[None]
        return lam, v
    lam = np.full((nT, N), np.nan)
    for t in range(nT):
        try:
            w = sla.eigh(C[t], C[t0], eigvals_only=True)
            lam[t] = np.sort(w)[::-1]
        except np.linalg.LinAlgError:
            pass
    return lam, None


def effective_mass(c, dt=1):
    c = np.asarray(c, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(c[:-dt] / c[dt:]) / dt


def is_positive_definite(M, tol=0.0):
    M = 0.5 * (M + M.T)
    return bool(np.linalg.eigvalsh(M).min() > tol)
