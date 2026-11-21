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


# --------------------------------------------------------------------------------------------
# Quark-line reference contractions: explicit Wick enumeration over the nonzero tensor entries,
# explicit SO(8) adjoint matrices from the definition 2 Tr[T^a V T^b V^dag], python loops.
def _adj_ref(V):
    R = np.zeros((8, 8))
    for a in range(8):
        for b in range(8):
            R[a, b] = (2 * np.trace(TA[a] @ V @ TA[b] @ V.conj().T)).real
    return R


def G5_12():
    from ..gamma import G5
    return np.kron(G5, np.eye(3))


def _blocks(S_by_flavour, t, nf=3):
    n = nf * 12
    fw = np.zeros((n, n), dtype=complex)
    bw = np.zeros((n, n), dtype=complex)
    g5 = G5_12()
    for f, S in S_by_flavour.items():
        s = S[t].reshape(12, 12)
        fw[f * 12:(f + 1) * 12, f * 12:(f + 1) * 12] = s
        bw[f * 12:(f + 1) * 12, f * 12:(f + 1) * 12] = g5 @ s.conj().T @ g5
    return fw, bw


def rmeson_reference(F, Fbar, S_by_flavour, W, tmax):
    C = np.zeros(tmax + 1, dtype=complex)
    for t in range(tmax + 1):
        fw, bw = _blocks(S_by_flavour, t)
        R = _adj_ref(W[t].conj().T)
        for a in range(F.shape[0]):
            for b in range(Fbar.shape[0]):
                if R[a, b] == 0:
                    continue
                acc = 0j
                Ai, Bi = np.nonzero(F[a])
                Ci, Di = np.nonzero(Fbar[b])
                for A, B in zip(Ai, Bi):
                    for Cc, D in zip(Ci, Di):
                        # <qbar_A q_B qbar_C q_D> connected = - S(t;0)_{B C} S(0;t)_{D A}
                        acc += -F[a, A, B] * Fbar[b, Cc, D] * fw[B, Cc] * bw[D, A]
                C[t] += R[a, b] * acc
    return C


def rbaryon_reference(F, Fbar, S_by_flavour, W, tmax, rho, sigma):
    from itertools import permutations
    C = np.zeros(tmax + 1, dtype=complex)
    perms = [(p, round(np.linalg.det(np.eye(3)[list(p)]))) for p in permutations(range(3))]
    for t in range(tmax + 1):
        fw, _ = _blocks(S_by_flavour, t)
        R = _adj_ref(W[t].conj().T)
        for a in range(F.shape[0]):
            src = list(zip(*np.nonzero(F[a, rho])))
            for b in range(Fbar.shape[0]):
                if abs(R[a, b]) < 1e-15:
                    continue
                snk = list(zip(*np.nonzero(Fbar[b, sigma])))
                acc = 0j
                for (A, B, Cc) in src:
                    fa = F[a, rho, A, B, Cc]
                    for (A2, B2, C2) in snk:
                        fb = Fbar[b, sigma, A2, B2, C2]
                        primed = (A2, B2, C2)
                        for p, sg in perms:
                            acc += sg * fa * fb * fw[A, primed[p[0]]] * fw[B, primed[p[1]]] * fw[Cc, primed[p[2]]]
                C[t] += R[a, b] * acc
    return C
