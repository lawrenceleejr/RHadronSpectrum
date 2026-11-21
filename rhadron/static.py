"""Static (infinitely heavy) colour sources: temporal Wilson lines, adjoint representation."""
import numpy as np

from .backend import get_xp
from .gauge.field import dag, mul, shift
from .gauge.smear import HYP_PARAMS, T, hyp_links


def gell_mann():
    l = np.zeros((8, 3, 3), dtype=complex)
    l[0][0, 1] = l[0][1, 0] = 1
    l[1][0, 1], l[1][1, 0] = -1j, 1j
    l[2][0, 0], l[2][1, 1] = 1, -1
    l[3][0, 2] = l[3][2, 0] = 1
    l[4][0, 2], l[4][2, 0] = -1j, 1j
    l[5][1, 2] = l[5][2, 1] = 1
    l[6][1, 2], l[6][2, 1] = -1j, 1j
    l[7][0, 0] = l[7][1, 1] = 1 / np.sqrt(3)
    l[7][2, 2] = -2 / np.sqrt(3)
    return l


TA = gell_mann() / 2.0  # generators, Tr(T^a T^b) = delta/2


def to_adjoint(W):
    """W_adj^{ab} = 2 Re Tr[T^a W T^b W^dag]  (real orthogonal 8x8, det 1)."""
    xp = get_xp(W)
    t = xp.asarray(TA)
    WtW = mul(mul(W[..., None, :, :], t), dag(W)[..., None, :, :])  # [..., b, 3, 3] = W T^b W^dag
    return 2.0 * xp.einsum("aij,...bji->...ab", t, WtW).real


def static_links(U, action="HYP2", n_proj=10):
    """Temporal links used in the static propagator: 'HYP2', 'HYP1', 'APE'(=HYP with a2=a3=0) or 'WILSON'."""
    if action == "WILSON":
        return U[T]
    if action in HYP_PARAMS:
        return hyp_links(U, HYP_PARAMS[action], dirs=(T,), n_proj=n_proj)[T]
    if action == "APE":  # 4D APE-like single level, alpha = 0.6 (staples in all 3 orthogonal dirs)
        return hyp_links(U, (0.6, 0.0, 0.0), dirs=(T,), n_proj=n_proj)[T]
    raise ValueError(action)


def wilson_lines(V4, t0, tmax):
    """W[dt](x) = V4(x,t0) V4(x,t0+1) ... V4(x,t0+dt-1), dt = 0..tmax, for a temporal link field
    V4[t,z,y,x,3,3].  Returns array [tmax+1, Lz, Ly, Lx, 3, 3]."""
    xp = get_xp(V4)
    Lt = V4.shape[0]
    W = xp.empty((tmax + 1,) + V4.shape[1:], dtype=V4.dtype)
    cur = xp.broadcast_to(xp.eye(3, dtype=V4.dtype), V4.shape[1:]).copy()
    W[0] = cur
    for dt in range(1, tmax + 1):
        cur = mul(cur, V4[(t0 + dt - 1) % Lt])
        W[dt] = cur
    return W
