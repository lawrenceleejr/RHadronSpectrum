"""The cubic group O_h (48 elements) acting on 3-vectors, its 10 real irreps (explicit matrices), and
row/transfer projectors.  The double cover O_h^D is in oh_double.py.

Irreps: A1, A2, E, T1, T2 (rotation group O) x g/u (inversion).  Matrices are real orthogonal.
"""
from functools import lru_cache
from itertools import permutations, product

import numpy as np

IRREPS = ["A1g", "A2g", "Eg", "T1g", "T2g", "A1u", "A2u", "Eu", "T1u", "T2u"]
DIM = {"A1": 1, "A2": 1, "E": 2, "T1": 3, "T2": 3}


@lru_cache(maxsize=None)
def elements():
    """All 48 signed 3x3 permutation matrices (integer)."""
    out = []
    for p in permutations(range(3)):
        for s in product((1, -1), repeat=3):
            R = np.zeros((3, 3), dtype=int)
            for r in range(3):
                R[r, p[r]] = s[r]
            out.append(R)
    return tuple(out)


def perm_sign(R):
    P = np.abs(R)
    return int(round(np.linalg.det(P)))


def _rot_rep(name, R0):
    """Irrep matrices of the proper rotation R0 for the rotation group O."""
    if name == "A1":
        return np.ones((1, 1))
    if name == "A2":
        return np.array([[float(perm_sign(R0))]])
    if name == "T1":
        return R0.astype(float)
    if name == "T2":
        return perm_sign(R0) * R0.astype(float)  # T2 = T1 x A2 (real, orthogonal)
    if name == "E":
        # basis f1 = (2z^2 - x^2 - y^2)/sqrt(6), f2 = (x^2 - y^2)/sqrt(2); (R f)(r) = f(R^-1 r)
        B = np.array([[-1, -1, 2], [1, -1, 0]], dtype=float) / np.array([[np.sqrt(6)], [np.sqrt(2)]])
        # f_k(r) = sum_i B[k,i] r_i^2 ; f_k(R^T r) = sum_i B[k,i] (sum_j R_ji r_j)^2 = sum_j B[k,i] R_ji^2 r_j^2
        Rinv = R0.T.astype(float)
        Q = B @ (Rinv ** 2)  # (R f_k)(r) = sum_j Q[k, j] r_j^2
        # R f_k = sum_l D[l, k] f_l  =>  Q = D^T B  =>  D = (Q B^T)^T   (rows of B orthonormal)
        return (Q @ B.T).T
    raise ValueError(name)


def rep(irrep, R):
    """Matrix of group element R (3x3 integer) in irrep (e.g. 'T1u')."""
    base, par = irrep[:-1], irrep[-1]
    det = int(round(np.linalg.det(R)))
    R0 = R * det
    D = _rot_rep(base, R0)
    if det == -1 and par == "u":
        D = -D
    return D


def dim(irrep):
    return DIM[irrep[:-1]]


def character(irrep, R):
    return float(np.trace(rep(irrep, R)))


def index_of(R):
    for k, g in enumerate(elements()):
        if np.array_equal(g, R):
            return k
    raise KeyError(R)


def mult_table():
    G = elements()
    return np.array([[index_of(a @ b) for b in G] for a in G])


def projector(irrep, T_ops, row=0, col=None):
    """Row (col=None -> col=row) or transfer projector P^Gamma_{row,col} = d/|G| sum_g D_{row,col}(g) T(g)
    for a representation given as a list of matrices T_ops (one per element, same order as elements())."""
    col = row if col is None else col
    G = elements()
    d = dim(irrep)
    P = sum(rep(irrep, g)[row, col] * T for g, T in zip(G, T_ops))
    return d / len(G) * P
