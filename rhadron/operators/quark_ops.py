"""Local quark operators at the static source site as explicit tensors over
A = (flavour, spin, colour), size NF*12.  Flavours: 0 = u, 1 = d, 2 = s.

Meson   O^a     = qbar_A F[a, A, B] q_B                      (a = adjoint index of the octet q qbar)
Baryon  O^a_rho = F[a, rho, A, B, C] q_A q_B q_C            (rho = free spin index of the light cloud)
"""
from itertools import permutations

import numpy as np

from ..gamma import C as CC
from ..gamma import G, G5, ONE, P_MINUS, P_PLUS
from ..static import TA

NF = 3
EPS = np.zeros((3, 3, 3))
for p in permutations(range(3)):
    EPS[p] = np.linalg.det(np.eye(3)[list(p)])

# meson Dirac structures: name -> (list of Gamma for the components (rows) of the irrep), light j^P)
MESON_GAMMAS = {
    "g5": ([G5], "A1", "0-"),
    "g4g5": ([G[3] @ G5], "A1", "0-"),
    "1": ([ONE], "A1", "0+"),
    "g4": ([G[3]], "A1", "0+"),
    "gi": ([G[i] for i in range(3)], "T1", "1-"),
    "g4gi": ([G[3] @ G[i] for i in range(3)], "T1", "1-"),
    "g5gi": ([G5 @ G[i] for i in range(3)], "T1", "1+"),
    "g4g5gi": ([G[3] @ G5 @ G[i] for i in range(3)], "T1", "1+"),
}


def flavour_matrix(pair):
    """qbar_f1 q_f2 flavour matrix for a named meson flavour content."""
    phi = np.zeros((NF, NF))
    if pair == "ud":  # dbar u  (I = 1, I3 = +1):  O = dbar Gamma T u
        phi[1, 0] = 1
    elif pair == "us":  # sbar u  (I = 1/2)
        phi[2, 0] = 1
    elif pair == "ss":
        phi[2, 2] = 1
    elif pair == "uu+dd":  # (ubar u + dbar d)/sqrt2  (I = 0, light)
        phi[0, 0] = phi[1, 1] = 1 / np.sqrt(2)
    else:
        raise ValueError(pair)
    return phi


def meson_tensor(Gamma, phi, colour="octet"):
    """F[a, (f,s,c), (f',s',c')] = phi[f,f'] Gamma[s,s'] T^a[c,c'] (octet) or delta (singlet, a=0)."""
    col = TA if colour == "octet" else np.eye(3)[None] / np.sqrt(3)
    F = np.einsum("fg,st,acd->afscgtd", phi, Gamma, col)
    n = col.shape[0]
    return F.reshape(n, NF * 12, NF * 12)


def meson_bar(F):
    """Obar = qbar Fbar q with Fbar[a] = g4 F[a]^dag g4 (spin), so that Obar = O^dag (Minkowski)."""
    n = F.shape[0]
    Fr = F.reshape(n, NF, 4, 3, NF, 4, 3)
    Fd = np.conj(Fr).transpose(0, 4, 5, 6, 1, 2, 3)  # dagger in (A, B)
    Fd = np.einsum("su,afucgvd,vt->afscgtd", G[3], Fd, G[3])
    return Fd.reshape(n, NF * 12, NF * 12)


# ----------------------------------------------------------------------------------------------
# Baryons: colour structures.  Octets in 3x3x3: K1 (antisymmetric diquark, from 3bar x 3) and
# K2 (symmetric diquark, from 6 x 3).  Singlet: epsilon (ordinary baryons, used for validation).
def colour_tensor(kind):
    if kind == "octet_A":
        return np.einsum("ijk,ail->ajkl", EPS, TA)
    if kind == "octet_S":
        return np.einsum("ijl,aik->ajkl", EPS, TA) + np.einsum("ikl,aij->ajkl", EPS, TA)
    if kind == "singlet":
        return EPS[None] / np.sqrt(6)
    raise ValueError(kind)


def flavour_tensor(name):
    """phi[f1, f2, f3] for (q1 q2) q3 with the diquark first."""
    phi = np.zeros((NF, NF, NF))
    u, d, s = 0, 1, 2
    if name == "uuu":  # decuplet (I = 3/2)
        phi[u, u, u] = 1
    elif name == "uud_A":  # octet (proton-like): [ud] u
        phi[u, d, u], phi[d, u, u] = 1, -1
    elif name == "uud_S":  # octet / decuplet mixture: {ud} u  (projected by the flavour irreps below)
        phi[u, d, u] = phi[d, u, u] = 1
    elif name == "uds_singlet":
        phi = EPS.copy() / np.sqrt(6)
    elif name == "uds_Lambda8":  # octet Lambda-like:  [ud] s  - ... (mixed symmetry, Lambda)
        phi[u, d, s], phi[d, u, s] = 2, -2
        phi[d, s, u], phi[s, d, u] = 1, -1
        phi[s, u, d], phi[u, s, d] = 1, -1
        phi /= np.sqrt(12)
    elif name == "uds_Sigma0_10":  # decuplet Sigma*0 (totally symmetric uds)
        for p in permutations((u, d, s)):
            phi[p] = 1 / np.sqrt(6)
    else:
        raise ValueError(name)
    return phi


def baryon_spin_tensor(diquark, j, parity=+1):
    """sigma[rho, s1, s2, s3]: light-cloud spin structure (q1^T C Gamma q2) (P q3).
    parity +1: P = P_+ (upper components), -1: P = P_-.
    diquark 'Cg5' (scalar): j = 1/2, rho = spinor (4).
    diquark 'Cgi' (vector): rho = (i, spinor) (12) projected with P^{3/2}_{ik} = delta_ik - g_i g_k/3
    (j = 3/2); or j = 1/2 via sum_i (C g_i) x (g_i g5 q3), rho = spinor (4)."""
    P = P_PLUS if parity > 0 else P_MINUS
    if diquark == "Cg5":
        if j != "1/2":
            raise ValueError("scalar diquark x quark has j = 1/2 only")
        return np.einsum("ab,rc->rabc", CC @ G5, P)
    if diquark == "Cgi":
        if j == "1/2":
            return sum(np.einsum("ab,rc->rabc", CC @ G[i], P @ G[i] @ G5) for i in range(3))
        out = []
        for i in range(3):
            acc = 0
            for k in range(3):
                Pik = (i == k) * ONE - G[i] @ G[k] / 3.0
                acc = acc + np.einsum("ab,rc->rabc", CC @ G[k], P @ Pik)
            out.append(acc)
        return np.concatenate(out, axis=0)
    raise ValueError(diquark)


def baryon_tensor(colour, flavour, diquark, j, parity=+1):
    """F[a, rho, A, B, C] with A = (f, s, c)."""
    K = colour_tensor(colour)
    phi = flavour_tensor(flavour)
    sig = baryon_spin_tensor(diquark, j, parity)
    F = np.einsum("aijk,fgh,rstu->arfsigtjhuk", K, phi, sig)
    na, nr = K.shape[0], sig.shape[0]
    return F.reshape(na, nr, NF * 12, NF * 12, NF * 12)


def baryon_bar(F):
    """Fbar with O^dag = qbar_C' qbar_B' qbar_A' Fbar[A', B', C'] (q^dag = qbar g4 on each quark).
    The free indices (a, rho) are simply complex conjugated: C_{rho sigma} = <O_rho O_sigma^dag>."""
    na, nr = F.shape[:2]
    Fr = np.conj(F.reshape(na, nr, NF, 4, 3, NF, 4, 3, NF, 4, 3))
    g4 = G[3]
    Fb = np.einsum("Ss,Tt,Uu,arfsigthuk->arfSigThUk", g4, g4, g4, Fr)
    return Fb.reshape(na, nr, NF * 12, NF * 12, NF * 12)
