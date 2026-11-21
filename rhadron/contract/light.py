"""Zero-momentum light-hadron correlators from point-to-all propagators (M3 validation).

S[t, z, y, x, s, a, s0, a0] = S(x, t; x0) for one flavour (degenerate u = d).
Meson:   C_G(t) = -sum_x Tr[G S(x;0) Gbar S(0;x)],  S(0;x) = g5 S(x;0)^dag g5,  Gbar = g4 G^dag g4
         (sign convention so that the pion correlator sum |S|^2 is positive)
Nucleon: O = eps_abc (u_a^T C g5 d_b) u_c, P+ projected; Wick contractions with the same tensor
         conventions as rhadron.contract.hadron (direct minus u-exchange), summed over x.
"""
import numpy as np

from ..backend import get_xp
from ..gamma import C as CC
from ..gamma import G, G5, P_PLUS
from ..operators.quark_ops import EPS


def _bwd(S, xp):
    g5 = xp.asarray(G5)
    Sd = S.conj().transpose(0, 1, 2, 3, 6, 7, 4, 5)  # [.., s0 a0, s a]
    return xp.einsum("st,...tauc,uv->...savc", g5, Sd, g5)


def meson(S, Gamma, t0=0):
    xp = get_xp(S)
    Gm = xp.asarray(Gamma)
    Gb = xp.asarray(G[3] @ Gamma.conj().T @ G[3])
    Sb = _bwd(S, xp)
    X = xp.einsum("su,tzyxuavb->tzyxsavb", Gm, S)
    X = xp.einsum("tzyxsavb,vw->tzyxsawb", X, Gb)
    c = -xp.einsum("tzyxsawb,tzyxwbsa->t", X, Sb)
    return xp.roll(c, -t0)


def nucleon_tensor():
    """F[rho, (s,c)_u1, (s,c)_d, (s,c)_u2] for eps (u^T C g5 d) P+ u."""
    D = CC @ G5
    F = np.einsum("abc,st,ru->rsatbuc", EPS, D, P_PLUS)
    return F.reshape(4, 12, 12, 12)


def nucleon_bar(F):
    Fr = np.conj(F.reshape(4, 4, 3, 4, 3, 4, 3))
    g4 = G[3]
    return np.einsum("Ss,Tt,Uu,rsatbuc->rSaTbUc", g4, g4, g4, Fr).reshape(4, 12, 12, 12)


def nucleon(S, t0=0):
    """C(t) = sum_x sum_rho <O_rho(x,t) O_rho^dag(0)> (P+ projected)."""
    xp = get_xp(S)
    F = xp.asarray(nucleon_tensor())
    Fb = xp.asarray(nucleon_bar(nucleon_tensor()))
    Lt = S.shape[0]
    Sm = S.reshape(Lt, -1, 12, 12)
    out = xp.zeros(Lt, dtype=complex)
    for t in range(Lt):
        U = Sm[t]  # [V3, 12, 12]
        X = xp.einsum("rABC,vAa->rvaBC", F, U)
        Y = xp.einsum("rvaBC,vBb->rvabC", X, U)
        direct = xp.einsum("rvabC,vCc,rabc->", Y, U, Fb)
        exch = xp.einsum("rvabC,vCc,rcba->", Y, U, Fb)  # u1 <-> u2 exchange at the source
        out[t] = direct - exch
    return xp.roll(out, -t0)
