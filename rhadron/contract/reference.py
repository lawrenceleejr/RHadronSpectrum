"""Slow, explicit reference contractions for tiny lattices (CPU).  Written independently of the
vectorised production code: site loops, fundamental-representation traces, no adjoint matrices."""
import numpy as np

from ..operators.paths import SHAPES, orbit
from ..static import TA


def _link(V, mu, n, L):
    return V[mu][n[3] % L[0], n[2] % L[1], n[1] % L[2], n[0] % L[3]]


def path_matrix(V, path, x):
    """Product of links along path from site x = (x, y, z, t)."""
    L = V.shape[1:5]
    n = list(x)
    P = np.eye(3, dtype=complex)
    for d in path:
        mu = abs(d) - 1
        if d > 0:
            P = P @ _link(V, mu, n, L)
            n[mu] += 1
        else:
            n[mu] -= 1
            P = P @ _link(V, mu, n, L).conj().T
    return P


def traceless(M):
    return M - np.trace(M) / 3 * np.eye(3)


def gluelump_corr_reference(V, V4, path_coeffs, cs, tmax):
    """C(t) = mean_{x,t0} 2 Re Tr[X(t0+t)^dag W^dag X(t0) W] for ONE operator X = sum_k c_k X_{S_k},
    with X_S = traceless((P - s P^dag)/2) (s = cs).  path_coeffs: list of (path, coefficient)."""
    Lt, Lz, Ly, Lx = V.shape[1:5]
    C = np.zeros(tmax + 1)

    def X(x):
        M = np.zeros((3, 3), dtype=complex)
        for p, c in path_coeffs:
            P = path_matrix(V, p, x)
            M += c * traceless(0.5 * (P + cs * P.conj().T))
        return M

    for t0 in range(Lt):
        for z in range(Lz):
            for y in range(Ly):
                for xx in range(Lx):
                    Xs = X((xx, y, z, t0))
                    W = np.eye(3, dtype=complex)
                    for dt in range(tmax + 1):
                        if dt > 0:
                            W = W @ V4[(t0 + dt - 1) % Lt, z, y, xx]
                        Xk = X((xx, y, z, (t0 + dt) % Lt))
                        C[dt] += 2 * np.trace(Xk.conj().T @ W.conj().T @ Xs @ W).real
    return C / (Lt * Lz * Ly * Lx)
