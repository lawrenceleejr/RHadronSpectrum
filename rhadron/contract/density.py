"""Light-quark densities around the static gluino: three-point functions with a local bilinear
J = qbar Gamma_J q inserted at (y, tau) between an R-meson source at (x0, t0) and sink at (x0, t1).

  C3_q(y)    = - sum_ab R^ab(W^dag) Tr[F^a S(x1;y) Gamma_J S(y;x0) Fbar^b S(x0;x1)]   (on the quark)
  C3_qbar(y) = - sum_ab R^ab(W^dag) Tr[F^a S(x1;x0) Fbar^b S(x0;y) Gamma_J S(y;x1)]   (on the antiquark)

W: static line x0, t0 -> t1.  F^a = Gamma (x) T^a in spin-colour (single flavour pair: I=1 d-bar u, with
degenerate u, d; the two insertions are the u and d-bar densities).  Inputs:
  Sy0[y]  = S(y, tau; x0, t0)  smeared source at x0, point sink y          [V3, 4,3,4,3]
  Sy1[y]  = S(y, tau; x0, t1)  partner source                               [V3, 4,3,4,3]
  S10     = S(x0, t1; x0, t0)  smeared both ends (site series at t = t1 - t0) [4,3,4,3]
All other legs follow from gamma5-hermiticity.  Normalised density: C3 / C2(t1 - t0).
"""
import numpy as np

from ..backend import get_xp
from ..gamma import G, G5
from ..static import TA, to_adjoint

G5_12 = np.kron(G5, np.eye(3))


def _m(S):
    return S.reshape(S.shape[:-4] + (12, 12))


def _herm5(xp, S12):
    g5 = xp.asarray(G5_12)
    return g5 @ S12.conj().swapaxes(-1, -2) @ g5


def octet_tensors(Gamma):
    F = np.einsum("st,aij->asitj", Gamma, TA).reshape(8, 12, 12)
    Gb = G[3] @ Gamma.conj().T @ G[3]
    Fb = np.einsum("st,aij->asitj", Gb, TA).reshape(8, 12, 12)
    return F, Fb


def density_3pt(Sy0, Sy1, S10, W, Gamma, GammaJ):
    """Returns (C3_q[y], C3_qbar[y]) over the insertion timeslice, xp-generic (numpy or cupy)."""
    xp = get_xp(Sy0)
    F, Fb = (xp.asarray(x) for x in octet_tensors(Gamma))
    J = xp.asarray(np.kron(GammaJ, np.eye(3)))
    R = xp.asarray(to_adjoint(W.conj().T if hasattr(W, "conj") else W))  # R(W^dag)
    y0, y1, s10 = _m(Sy0), _m(Sy1), _m(S10)
    s1y = _herm5(xp, y1)          # S(x1; y)
    s0y = _herm5(xp, y0)          # S(x0; y)
    s01 = _herm5(xp, s10)         # S(x0; x1)
    # quark line: Tr[F^a M Fbar^b S01], M = S(x1;y) J S(y;x0)  ->  sum_ij M_ij K_ji, K = sum R^ab Fbar^b S01 F^a
    M = s1y @ J @ y0
    K = xp.einsum("ab,bjk,kl,ali->ji", R, Fb, s01, F)
    cq = -xp.einsum("yij,ji->y", M, K)
    # antiquark line: Tr[F^a S10 Fbar^b M'], M' = S(x0;y) J S(y;x1)
    Mp = s0y @ J @ y1
    Kp = xp.einsum("ab,aij,jk,bkl->il", R, F, s10, Fb)  # sum_ab R^ab F^a S10 Fbar^b
    cqb = -xp.einsum("il,yli->y", Kp, Mp)
    return cq, cqb


def density_3pt_reference(Sy0, Sy1, S10, W, Gamma, GammaJ):
    """Slow explicit version (loops over a, b and sites) for tests."""
    F, Fb = octet_tensors(Gamma)
    J = np.kron(GammaJ, np.eye(3))
    g5 = G5_12
    R = np.zeros((8, 8))
    Wd = W.conj().T
    for a in range(8):
        for b in range(8):
            R[a, b] = (2 * np.trace(TA[a] @ Wd @ TA[b] @ Wd.conj().T)).real
    s10 = S10.reshape(12, 12)
    s01 = g5 @ s10.conj().T @ g5
    n = Sy0.shape[0]
    cq, cqb = np.zeros(n, complex), np.zeros(n, complex)
    for y in range(n):
        Sy0y, Sy1y = Sy0[y].reshape(12, 12), Sy1[y].reshape(12, 12)
        S1y = g5 @ Sy1y.conj().T @ g5
        S0y = g5 @ Sy0y.conj().T @ g5
        for a in range(8):
            for b in range(8):
                cq[y] += -R[a, b] * np.trace(F[a] @ S1y @ J @ Sy0y @ Fb[b] @ s01)
                cqb[y] += -R[a, b] * np.trace(F[a] @ s10 @ Fb[b] @ S0y @ J @ Sy1y)
    return cq, cqb
