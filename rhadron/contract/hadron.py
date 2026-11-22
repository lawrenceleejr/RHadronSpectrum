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
from ..backend import get_xp
from ..static import to_adjoint
from ..operators.quark_ops import NF

PERMS = [(p, int(round(np.linalg.det(np.eye(3)[list(p)])))) for p in permutations(range(3))]


def big_propagators(S_by_flavour, t):
    """Flavour-block-diagonal forward S(t;0) and backward S(0;t) as [NF*12, NF*12] (A = f, s, c)."""
    xp = get_xp(next(iter(S_by_flavour.values())))
    g5 = xp.asarray(G5)
    fwd = xp.zeros((NF, 4, 3, NF, 4, 3), dtype=complex)
    bwd = xp.zeros_like(fwd)
    for f, S in S_by_flavour.items():
        s = S[t]
        fwd[f, :, :, f] = s
        sb = xp.einsum("st,uatb->sbua", g5, s.conj())  # (S^dag)[s b; u a] with g5 on the left
        sb = xp.einsum("sbua,uv->sbva", sb, g5)
        bwd[f, :, :, f] = sb
    n = NF * 12
    return fwd.reshape(n, n), bwd.reshape(n, n)


def rmeson_block(F, Fbar, S_by_flavour, tmax):
    """B[t, a, b] = -Tr[F^a S(t;0) Fbar^b S(0;t)]  (connected)."""
    xp = get_xp(F)
    na = F.shape[0]
    out = xp.zeros((tmax + 1, na, Fbar.shape[0]), dtype=complex)
    for t in range(tmax + 1):
        fw, bw = big_propagators(S_by_flavour, t)
        fw, bw = xp.asarray(fw), xp.asarray(bw)
        X = xp.matmul(F, fw)  # F^a S(t;0)
        Y = xp.matmul(Fbar, bw)  # Fbar^b S(0;t)
        out[t] = -xp.einsum("aik,bki->ab", X, Y)
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
    return to_adjoint(W.conj().swapaxes(-1, -2))


def contract_rmeson(B, W):
    xp = get_xp(B)
    R = xp.asarray(adjoint_static(xp.asarray(W)))
    return xp.einsum("tab,tab->t", R, B)


def contract_rbaryon(B, W):
    xp = get_xp(B)
    R = xp.asarray(adjoint_static(xp.asarray(W)))
    return xp.einsum("tab,tarbs->trs", R, B)


def static_light(Gamma, S, W):
    """Fundamental static-light meson  C(t) = -Tr[Gamma (P+ W^dag) Gammabar S(0;t)]."""
    xp = get_xp(S)
    Gm = xp.asarray(Gamma)
    Gbar = xp.asarray(G[3] @ Gamma.conj().T @ G[3])
    g5, pp = xp.asarray(G5), xp.asarray(P_PLUS)
    W = xp.asarray(W)
    sb = xp.einsum("st,xuatb->xsbua", g5, S.conj())
    sb = xp.einsum("xsbua,uv->xsbva", sb, g5)  # S(0;t)[s,b; v,a]
    Gh = xp.einsum("st,xba->xsatb", pp, W.conj())  # P+ x W^dag  ([a,b] = conj(W[b,a]))
    X = xp.einsum("su,xuatb->xsatb", Gm, Gh)
    X = xp.einsum("xsatb,tv->xsavb", X, Gbar)
    return -xp.einsum("xsavb,xvbsa->x", X, sb)


def flavour_components(F, tol=0.0):
    """Split F[a, rho, A, B, C] (A = f*12 + spin*3 + colour) into {(f1, f2, f3): F_f[a, rho, 12, 12, 12]}."""
    na, nr = F.shape[:2]
    Fr = F.reshape(na, nr, NF, 12, NF, 12, NF, 12)
    out = {}
    for f1 in range(NF):
        for f2 in range(NF):
            for f3 in range(NF):
                blk = Fr[:, :, f1, :, f2, :, f3, :]
                if np.abs(blk).max() > tol:
                    out[(f1, f2, f3)] = blk
    return out


def rbaryon_block_fast(F, Fbar, S_by_flavour, tmax):
    """Same as rbaryon_block, using flavour components: only permutations sigma with
    f_i == f'_sigma(i) contribute, each a 12-dimensional contraction."""
    xp = get_xp(next(iter(S_by_flavour.values())))
    Fc = {k: xp.asarray(v) for k, v in (F if isinstance(F, dict) else flavour_components(F)).items()}
    Fbc = {k: xp.asarray(v) for k, v in (Fbar if isinstance(Fbar, dict) else flavour_components(Fbar)).items()}
    na, nr = next(iter(Fc.values())).shape[:2]
    nb, ns = next(iter(Fbc.values())).shape[:2]
    out = xp.zeros((tmax + 1, na, nr, nb, ns), dtype=complex)
    for t in range(tmax + 1):
        P = {f: S[t].reshape(12, 12) for f, S in S_by_flavour.items()}
        for fl, Fa in Fc.items():
            X = xp.tensordot(Fa, P[fl[0]], axes=([2], [0]))
            X = xp.tensordot(X, P[fl[1]], axes=([2], [0]))
            X = xp.tensordot(X, P[fl[2]], axes=([2], [0]))  # [a, r, A', B', C'] at flavours fl
            for flb, Fb in Fbc.items():
                for p, sg in PERMS:
                    # source slot i (flavour fl[i]) contracts with sink slot p[i] (flavour flb[p[i]])
                    if any(fl[i] != flb[p[i]] for i in range(3)):
                        continue
                    # X index i pairs with Fb index p[i]:  Fb_perm[..., i] = Fb[..., p[i]]
                    Fbp = xp.transpose(Fb, (0, 1) + tuple(2 + p[i] for i in range(3)))
                    out[t] += sg * xp.tensordot(X, Fbp, axes=([2, 3, 4], [2, 3, 4]))
    return out


def static_light_matrix(Gam_snk, Gam_src, S, W):
    """C(t) = -Tr[Gam_snk (P+ W^dag) Gam_src_bar S(0;t)] for a general light-line site propagator S[t]
    (e.g. with derivative insertions at both ends); static_light() is the diagonal special case."""
    xp = get_xp(S)
    Gm = xp.asarray(Gam_snk)
    Gbar = xp.asarray(G[3] @ Gam_src.conj().T @ G[3])
    g5, pp = xp.asarray(G5), xp.asarray(P_PLUS)
    W = xp.asarray(W)
    sb = xp.einsum("st,xuatb->xsbua", g5, S.conj())
    sb = xp.einsum("xsbua,uv->xsbva", sb, g5)
    Gh = xp.einsum("st,xba->xsatb", pp, W.conj())
    X = xp.einsum("su,xuatb->xsatb", Gm, Gh)
    X = xp.einsum("xsatb,tv->xsavb", X, Gbar)
    return -xp.einsum("xsavb,xvbsa->x", X, sb)


# P-wave static-light operators  O = qbar Gamma_i D_j h  (derivative on the light quark):
#   P-  (j = 1/2): sum_i gamma_i D_i ;   P+ (j = 3/2, E irrep): gamma_x D_x - gamma_y D_y (+ cyclic)
PWAVE = {
    "Pm_D": [[(1.0, i, i) for i in range(3)]],
    "Pp_E": [[(1.0, 0, 0), (-1.0, 1, 1)], [(1.0, 1, 1), (-1.0, 2, 2)], [(1.0, 2, 2), (-1.0, 0, 0)]],
}


def static_light_pwave(SD, W):
    """SD[(j, l)][t] = D_j^snk S D_l^src at the static site.  Returns {name: C(t)} averaged over the
    irrep rows; C = sum_{(c,i,j),(c',k,l)} c c' C_{(gamma_i D_j),(gamma_k D_l)}."""
    out = {}
    for name, rows in PWAVE.items():
        acc = 0
        for row in rows:
            for (c1, i, j) in row:
                for (c2, k, l) in row:
                    acc = acc + c1 * c2 * static_light_matrix(G[i], G[k], SD[(j, l)], W)
        out[name] = acc / len(rows)
    return out
