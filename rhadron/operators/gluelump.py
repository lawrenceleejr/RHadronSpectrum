"""Gluelump (adjoint static source + glue) operators and correlators.

Operator for a closed spatial path S at site x:  X_S(x) = traceless part of
  (P_S - P_S^dag)/2   (C = -1)   or   (P_S + P_S^dag)/2   (C = +1).
Its adjoint components x^a are real: X = i x^a T^a (C=-) or X = x^a T^a (C=+).
Irrep operators: O^{Gamma,C}_{lambda, m} = sum_k v^{(m)}_{lambda,k} x_{S_k}, with v from row/transfer
projectors on the (signed-permutation) orbit representation.

Correlator (gauge invariant):  C_ij(t) = < sum_ab x_i^a(x, t0+t) R^ab(W^dag) x_j^b(x, t0) >
  = 2 Tr[X_i(t0+t)^dag W^dag X_j(t0) W],  W = V4(x,t0) ... V4(x,t0+t-1).
Averaged over x, t0, rows; returned per (irrep, C) as a matrix over (shape, multiplicity, smearing).
"""
import numpy as np

from ..backend import get_xp
from ..gauge.field import dag, mul
from ..groups.oh import IRREPS, dim, projector
from ..static import TA, to_adjoint
from .paths import SHAPES, orbit, path_field, rep_matrices

C_LABEL = {-1: "-", +1: "+"}


def irrep_coefficients(path, tol=1e-10):
    """For a shape: dict (irrep, C) -> array v[row, mult, n_paths] (orthonormal in the orbit space)."""
    keys, action = orbit(path)
    n = len(keys)
    out = {}
    for cs in (-1, +1):
        T = rep_matrices(action, n, cs)
        for ir in IRREPS:
            P00 = projector(ir, T, 0, 0)
            w, u = np.linalg.eigh(0.5 * (P00 + P00.T))
            base = u[:, w > 0.5].T  # [mult, n]
            if base.shape[0] == 0:
                continue
            d = dim(ir)
            v = np.zeros((d, base.shape[0], n))
            v[0] = base
            for lam in range(1, d):
                v[lam] = (projector(ir, T, lam, 0) @ base.T).T
            out[(ir, C_LABEL[cs])] = v
    return keys, out


def adjoint_components(X, c_sign):
    """Real adjoint components of traceless X: C=- (anti-Hermitian) x^a = 2 Im Tr[T^a X];
    C=+ (Hermitian) x^a = 2 Re Tr[T^a X]."""
    xp = get_xp(X)
    t = xp.asarray(TA)
    tr = xp.einsum("aij,...ji->...a", t, X)
    return 2.0 * (tr.imag if c_sign < 0 else tr.real)


def path_components(V, path):
    """Both C projections of path P_S: returns {-1: x^a, +1: x^a} with shape [t,z,y,x,8]."""
    P = path_field(V, path)
    return {-1: adjoint_components(0.5 * (P - dag(P)), -1),
            +1: adjoint_components(0.5 * (P + dag(P)), +1)}


def build_operators(V_levels, shapes=None, dtype=np.float64):
    """Irrep-projected gluelump operators.

    V_levels: list of spatially smeared link fields (one per smearing level).
    Returns (ops, labels): ops[(irrep, C)] = array [n_op, row, t, z, y, x, 8];
    labels[(irrep, C)] = list of (shape, mult, level).
    """
    shapes = shapes or list(SHAPES)
    xp = get_xp(V_levels[0])
    ops, labels = {}, {}
    for sname in shapes:
        keys, coeffs = irrep_coefficients(SHAPES[sname])
        for lev, V in enumerate(V_levels):
            comps = [path_components(V, k) for k in keys]
            for (ir, cl), v in coeffs.items():
                cs = -1 if cl == "-" else +1
                X = xp.stack([c[cs] for c in comps])  # [n_paths, t,z,y,x,8]
                o = xp.tensordot(xp.asarray(v), X, axes=([2], [0]))  # [row, mult, t,z,y,x,8]
                o = xp.moveaxis(o, 1, 0).astype(dtype)  # [mult, row, ...]
                ops.setdefault((ir, cl), []).append(o)
                labels.setdefault((ir, cl), []).extend((sname, m, lev) for m in range(o.shape[0]))
    ops = {k: xp.concatenate(v, axis=0) for k, v in ops.items()}
    return ops, labels


def correlators(ops, V4, tmax, t0_list=None):
    """C[(irrep,C)][t, i, j] = mean_{x, t0, row} x_i(t0+t) . R(W^dag) x_j(t0); t = 0..tmax.
    Hermitised (C_ij + C_ji)/2 (time-reversal / backward propagation)."""
    xp = get_xp(V4)
    Lt = V4.shape[0]
    t0_list = range(Lt) if t0_list is None else t0_list
    out = {k: xp.zeros((tmax + 1, o.shape[0], o.shape[0])) for k, o in ops.items()}
    nsite = None
    for t0 in t0_list:
        W = xp.broadcast_to(xp.eye(3, dtype=V4.dtype), V4.shape[1:]).copy()
        for dt in range(tmax + 1):
            if dt > 0:
                W = mul(W, V4[(t0 + dt - 1) % Lt])
            R = to_adjoint(dag(W))  # [z,y,x,8,8]
            t1 = (t0 + dt) % Lt
            for k, o in ops.items():
                src = xp.einsum("zyxab,irzyxb->irzyxa", R, o[:, :, t0].astype(np.float64))
                snk = o[:, :, t1].astype(np.float64)
                c = xp.einsum("irzyxa,jrzyxa->ij", snk, src)
                out[k][dt] += c
            nsite = R.shape[0] * R.shape[1] * R.shape[2]
    for k, o in ops.items():
        nrm = len(list(t0_list)) * nsite * o.shape[1]
        c = out[k] / nrm
        out[k] = 0.5 * (c + c.swapaxes(1, 2))
    return out


def _slice_ops(V_levels, t, shapes, dtype):
    """Operators on timeslice t only: dict key -> [n_op, row, z, y, x, 8]."""
    ops, labels = build_operators([V[:, t:t + 1] for V in V_levels], shapes=shapes, dtype=dtype)
    return {k: o[:, :, 0] for k, o in ops.items()}, labels


def measure(V_levels, V4_by_action, tmax, shapes=None, dtype=np.float32):
    """Production gluelump correlators streamed over timeslices (memory ~ (tmax+1) slices of ops).

    V_levels: spatially smeared link fields (list, one per smearing level).
    V4_by_action: {'HYP2': V4, ...} temporal links for the static line(s).
    Returns ({action: {key: C[t, i, j]}}, labels).  Normalised per site, source time and row.
    """
    xp = get_xp(V_levels[0])
    Lt = V_levels[0].shape[1]
    cache, labels = {}, None
    out = {a: {} for a in V4_by_action}
    nsite = None
    for t0 in range(Lt):
        for t in list(cache):
            if (t - t0) % Lt > tmax:
                del cache[t]
        for dt in range(tmax + 1):
            t1 = (t0 + dt) % Lt
            if t1 not in cache:
                cache[t1], labels = _slice_ops(V_levels, t1, shapes, dtype)
        src = cache[t0]
        for act, V4 in V4_by_action.items():
            W = xp.broadcast_to(xp.eye(3, dtype=V4.dtype), V4.shape[1:]).copy()
            for dt in range(tmax + 1):
                if dt > 0:
                    W = mul(W, V4[(t0 + dt - 1) % Lt])
                R = to_adjoint(dag(W))
                snk = cache[(t0 + dt) % Lt]
                for k in src:
                    s = xp.einsum("zyxab,irzyxb->irzyxa", R, src[k].astype(np.float64))
                    c = xp.einsum("irzyxa,jrzyxa->ij", snk[k].astype(np.float64), s)
                    acc = out[act].setdefault(k, xp.zeros((tmax + 1,) + c.shape))
                    acc[dt] += c
                nsite = R.shape[0] * R.shape[1] * R.shape[2]
    res = {}
    for act in out:
        res[act] = {}
        for k, c in out[act].items():
            c = c / (Lt * nsite * dim(k[0]))
            res[act][k] = 0.5 * (c + c.swapaxes(1, 2))
    return res, labels
