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


def baryon_corr(S_by_flavour, Fc, Fbc, chunk=1024):
    """General zero-momentum baryon correlator from flavour-decomposed operator tensors
    (rhadron.contract.hadron.flavour_components of a colour-SINGLET baryon_tensor / baryon_bar):
        C(t) = sum_x sum_rho <O_rho(x, t) O_rho(0)^dag>,
    all Wick contractions with flavour-consistent permutations (same conventions as rbaryon_block).
    S_by_flavour[f]: [t, z, y, x, 4, 3, 4, 3].  Independent code path from `nucleon`."""
    from itertools import permutations

    xp = get_xp(next(iter(S_by_flavour.values())))
    perms = [(p, int(round(np.linalg.det(np.eye(3)[list(p)])))) for p in permutations(range(3))]
    Fc = {k: xp.asarray(v[0]) for k, v in Fc.items()}  # drop the (singlet) colour-adjoint axis
    Fbc = {k: xp.asarray(v[0]) for k, v in Fbc.items()}
    S0 = next(iter(S_by_flavour.values()))
    Lt = S0.shape[0]
    P = {f: S.reshape(Lt, -1, 12, 12) for f, S in S_by_flavour.items()}
    V = P[next(iter(P))].shape[1]
    out = xp.zeros(Lt, dtype=complex)
    for t in range(Lt):
        for v0 in range(0, V, chunk):
            sl = slice(v0, min(V, v0 + chunk))
            for fl, Fa in Fc.items():
                X = xp.einsum("rABC,vAa->vraBC", Fa, P[fl[0]][t, sl])
                X = xp.einsum("vraBC,vBb->vrabC", X, P[fl[1]][t, sl])
                X = xp.einsum("vrabC,vCc->vrabc", X, P[fl[2]][t, sl])
                for flb, Fb in Fbc.items():
                    for p, sg in perms:
                        if any(fl[i] != flb[p[i]] for i in range(3)):
                            continue
                        Fbp = xp.transpose(Fb, (0,) + tuple(1 + p[i] for i in range(3)))
                        out[t] += sg * xp.einsum("vrabc,rabc->", X, Fbp)
    return out


def baryon_suite_tensors():
    """Colour-singlet zero-momentum baryon operators for the M3 nucleon cross-checks:
       N1 = eps (u^T C g5 d) P+ u,  N2 = eps (u^T C g4 g5 d) P+ u,  Delta++ = eps (u^T C g_k u) P+ P^{3/2}_{ik} u.
    Returns {name: (flavour components of F, of Fbar)} on the 3-flavour index space."""
    from ..contract.hadron import flavour_components
    from ..operators import quark_ops as qo
    out = {}
    for name, D in (("N1", CC @ G5), ("N2", CC @ G[3] @ G5)):
        F = np.zeros((1, 4, 36, 36, 36), dtype=complex)
        T = np.einsum("abc,st,ru->rsatbuc", EPS, D, P_PLUS).reshape(4, 12, 12, 12)
        F[0, :, 0:12, 12:24, 0:12] = T
        out[name] = (flavour_components(F), flavour_components(qo.baryon_bar(F)))
    F = qo.baryon_tensor("singlet", "uuu", "Cgi", "3/2")
    out["Delta"] = (flavour_components(F), flavour_components(qo.baryon_bar(F)))
    return out
