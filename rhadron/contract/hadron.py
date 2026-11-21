"""Production contractions at the static source site (all quark lines start and end at x).

Inputs per source site x and time t = 0..tmax:
  S[f][t]  = S_f(x, t0+t; x, t0)  as [4, 3, 4, 3] (spin, colour; spin0, colour0), smeared both ends
  W[t]     = V4(x,t0) ... V4(x,t0+t-1)  (static line, 3x3)
Backward propagator S_f(x, t0; x, t0+t) = g5 S_f^dag g5.

R-meson   C(t) = sum_ab R^ab(W^dag) B^ab(t),  B^ab = -Tr[F^a S(t;0) Fbar^b S(0;t)]
R-baryon  C_{rho sigma}(t) = sum_ab R^ab(W^dag) <O^a_rho(t) O^b_sigma(0)^dag>
Static-light (fundamental) C(t) = -Tr[Gamma (P+ x W^dag) Gammabar S(0;t)]
"""
from itertools import permutations

import numpy as np

from ..gamma import G, G5, P_PLUS
from ..static import to_adjoint
from ..operators.quark_ops import NF

PERMS = [(p, int(round(np.linalg.det(np.eye(3)[list(p)])))) for p in permutations(range(3))]


def big_propagators(S_by_flavour, t):
    """Flavour-block-diagonal forward S(t;0) and backward S(0;t) as [NF*12, NF*12] (A = f, s, c)."""
    fwd = np.zeros((NF, 4, 3, NF, 4, 3), dtype=complex)
    bwd = np.zeros_like(fwd)
    for f, S in S_by_flavour.items():
        s = S[t]
        fwd[f, :, :, f] = s
        sb = np.einsum("st,uatb->sbua", G5, s.conj())  # (S^dag)[s b; u a] with g5 on the left
        sb = np.einsum("sbua,uv->sbva", sb, G5)
        bwd[f, :, :, f] = sb
    n = NF * 12
    return fwd.reshape(n, n), bwd.reshape(n, n)


def rmeson_block(F, Fbar, S_by_flavour, tmax):
    """B[t, a, b] = -Tr[F^a S(t;0) Fbar^b S(0;t)]  (connected)."""
    na = F.shape[0]
    out = np.zeros((tmax + 1, na, Fbar.shape[0]), dtype=complex)
    for t in range(tmax + 1):
        fw, bw = big_propagators(S_by_flavour, t)
        X = np.einsum("aij,jk->aik", F, fw)  # F^a S(t;0)
        Y = np.einsum("bkl,li->bki", Fbar, bw)  # Fbar^b S(0;t)
        out[t] = -np.einsum("aik,bki->ab", X, Y)
    return out


def antisymmetrize3(Fb):
    """sum_perm sign(perm) Fb[..., perm(A', B', C')]."""
    out = 0
    for p, sg in PERMS:
        out = out + sg * np.transpose(Fb, (0, 1) + tuple(2 + q for q in p))
    return out


def rbaryon_block(F, Fbar, S_by_flavour, tmax):
    """B[t, a, rho, b, sigma] = <O^a_rho(t) O^b_sigma(0)^dag>  with all Wick contractions."""
    Fb_as = antisymmetrize3(Fbar)
    na, nr = F.shape[:2]
    out = np.zeros((tmax + 1, na, nr, Fbar.shape[0], Fbar.shape[1]), dtype=complex)
    for t in range(tmax + 1):
        fw, _ = big_propagators(S_by_flavour, t)
        X = np.tensordot(F, fw, axes=([2], [0]))  # [a, r, B, C, A']
        X = np.tensordot(X, fw, axes=([2], [0]))  # [a, r, C, A', B']
        X = np.tensordot(X, fw, axes=([2], [0]))  # [a, r, A', B', C']
        out[t] = np.tensordot(X, Fb_as, axes=([2, 3, 4], [2, 3, 4]))
    return out


def adjoint_static(W):
    """R(W^dag) for each t: [t, 8, 8]."""
    return to_adjoint(np.conj(np.swapaxes(W, -1, -2)))


def contract_rmeson(B, W):
    R = adjoint_static(W)
    return np.einsum("tab,tab->t", R, B)


def contract_rbaryon(B, W):
    R = adjoint_static(W)
    return np.einsum("tab,tarbs->trs", R, B)


def static_light(Gamma, S, W):
    """Fundamental static-light meson  C(t) = -Tr[Gamma (P+ W^dag) Gammabar S(0;t)]."""
    Gbar = G[3] @ Gamma.conj().T @ G[3]
    out = np.zeros(len(W), dtype=complex)
    for t in range(len(W)):
        s = S[t]
        sb = np.einsum("st,uatb->sbua", G5, s.conj())
        sb = np.einsum("sbua,uv->sbva", sb, G5)  # S(0;t)[s,b; v,a]
        Gh = np.einsum("st,ab->satb", P_PLUS, np.conj(W[t]).T)  # P+ x W^dag
        X = np.einsum("su,uatb->satb", Gamma, Gh)
        X = np.einsum("satb,tv->savb", X, Gbar)
        out[t] = -np.einsum("savb,vbsa->", X, sb)
    return out
