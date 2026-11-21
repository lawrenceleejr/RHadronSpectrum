"""CPU reference Wilson-clover Dirac operator (sparse, tiny lattices) and gauge-covariant quark
smearing.  Production propagators come from QUDA via PyQUDA; this module exists to test the
contraction code and to cross-check QUDA conventions on small lattices.

M = 1 - kappa * sum_mu [(1 - g_mu) U_mu(x) d_{x+mu,y} + (1 + g_mu) U_mu^dag(x-mu) d_{x-mu,y}]
      - kappa * c_sw * sum_{mu<nu} sigma_munu F_munu(x),   sigma_munu = i g_mu g_nu (mu != nu, Hermitian)
(sign of the clover term to be cross-checked against QUDA in the GPU tests)
F_munu = (Q_munu - Q_munu^dag) / (8 i)  with Q the sum of the four clover leaves.
Antiperiodic in time.  Propagator S(y, x) = M^-1 as a [site, 4, 3] x [4, 3] field (spin, colour).
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .backend import get_xp
from .gamma import G
from .gauge.field import ND, dag, mul, plaquette_field, shift


def clover_field(U, mu, nu):
    """F_munu(x) (Hermitian, traceless not enforced) from the 4 clover leaves."""
    xp = get_xp(U)
    Umu, Unu = U[mu], U[nu]
    l1 = plaquette_field(U, mu, nu)
    # leaf (nu, -mu)
    Umu_m = shift(Umu, mu, -1)
    l2 = mul(mul(Unu, dag(shift(shift(Umu, mu, -1), nu, 1))), mul(dag(shift(Unu, mu, -1)), Umu_m))
    # leaf (-mu, -nu)
    Unu_m = shift(Unu, nu, -1)
    l3 = mul(mul(dag(Umu_m), dag(shift(Unu_m, mu, -1))), mul(shift(shift(Umu, mu, -1), nu, -1), Unu_m))
    # leaf (-nu, mu)
    l4 = mul(mul(dag(Unu_m), shift(Umu, nu, -1)), mul(shift(shift(Unu, nu, -1), mu, 1), dag(Umu)))
    Q = l1 + l2 + l3 + l4
    return (Q - dag(Q)) / 8j


def _apbc(U):
    V = U.copy()
    V[3, -1] *= -1.0
    return V


def wilson_clover_matrix(U, kappa, csw, antiperiodic=True):
    """Sparse matrix M acting on vectors psi[t,z,y,x,spin,colour] flattened (C order)."""
    if antiperiodic:
        U = _apbc(U)
    shape = U.shape[1:5]
    V = int(np.prod(shape))
    n = V * 12
    idx = np.arange(V).reshape(shape)
    rows, cols, vals = [], [], []

    def add_block(src_sites, dst_sites, blk):  # blk[site, 4,3, 4,3]: (M psi)(dst) += blk psi(src)
        b = blk.reshape(V, 12, 12)
        r = (dst_sites[:, None, None] * 12 + np.arange(12)[None, :, None]).repeat(12, 2)
        c = (src_sites[:, None, None] * 12 + np.arange(12)[None, None, :]).repeat(12, 1)
        rows.append(r.ravel()), cols.append(c.ravel()), vals.append(b.ravel())

    eye4 = np.eye(4)
    site = idx.ravel()
    for mu in range(ND):
        fwd = shift(idx, mu, 1).ravel()
        bwd = shift(idx, mu, -1).ravel()
        Uf = U[mu].reshape(V, 3, 3)
        Ub = dag(shift(U[mu], mu, -1)).reshape(V, 3, 3)
        add_block(fwd, site, -kappa * np.einsum("st,xab->xsatb", eye4 - G[mu], Uf))
        add_block(bwd, site, -kappa * np.einsum("st,xab->xsatb", eye4 + G[mu], Ub))
    diag = np.broadcast_to(np.eye(12), (V, 12, 12)).astype(complex).copy()
    if csw != 0.0:
        Uc = U  # clover term uses the same (APBC) links; leaves are closed so the sign cancels
        for mu in range(ND):
            for nu in range(mu + 1, ND):
                F = clover_field(Uc, mu, nu).reshape(V, 3, 3)
                diag -= kappa * csw * np.einsum("st,xab->xsatb", 1j * G[mu] @ G[nu], F).reshape(V, 12, 12)
    add_block(site, site, diag.reshape(V, 4, 3, 4, 3))
    M = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    return M


def solve(M, b, tol=1e-13):
    """Iterative solve of M x = b (BiCGStab, GMRES fallback) to relative residual tol."""
    x, info = spla.bicgstab(M, b, rtol=tol, atol=0.0, maxiter=20000)
    if info != 0 or np.linalg.norm(M @ x - b) > 10 * tol * np.linalg.norm(b):
        x, info = spla.gmres(M, b, x0=x, rtol=tol, atol=0.0, restart=200, maxiter=200)
    r = np.linalg.norm(M @ x - b) / np.linalg.norm(b)
    if r > 1e-10:
        raise RuntimeError(f"reference solve did not converge: residual {r:.2e}")
    return x


def point_propagator(U, kappa, csw, x0, src_smear=None, snk_smear=None):
    """S[t,z,y,x, s,a, s0,a0] = (K_snk M^-1 K_src)(y, x0) for a point source at x0 = (x,y,z,t).
    src_smear/snk_smear: callables acting on a spinor field psi[t,z,y,x,4,3]."""
    shape = U.shape[1:5]
    M = wilson_clover_matrix(U, kappa, csw).tocsr()
    S = np.zeros(tuple(shape) + (4, 3, 4, 3), dtype=complex)
    for s0 in range(4):
        for a0 in range(3):
            b = np.zeros(tuple(shape) + (4, 3), dtype=complex)
            b[x0[3], x0[2], x0[1], x0[0], s0, a0] = 1.0
            if src_smear is not None:
                b = src_smear(b)
            psi = solve(M, b.ravel()).reshape(b.shape)
            if snk_smear is not None:
                psi = snk_smear(psi)
            S[..., s0, a0] = psi
    return S


def wuppertal(U, psi, alpha, n_iter, spatial_only=True):
    """Gauge-covariant Wuppertal/Gaussian smearing psi <- (psi + alpha H psi)/(1 + 6 alpha), n times,
    H psi(x) = sum_i [U_i(x) psi(x+i) + U_i^dag(x-i) psi(x-i)].  psi[t,z,y,x, (spin,) colour]."""
    xp = get_xp(psi)
    dirs = (0, 1, 2) if spatial_only else (0, 1, 2, 3)
    spin = psi.ndim == 6
    for _ in range(n_iter):
        h = 0
        for i in dirs:
            if spin:
                h = h + xp.einsum("...ab,...sb->...sa", U[i], shift(psi, i, 1))
                h = h + shift(xp.einsum("...ba,...sb->...sa", U[i].conj(), psi), i, -1)
            else:
                h = h + xp.einsum("...ab,...b->...a", U[i], shift(psi, i, 1))
                h = h + shift(xp.einsum("...ba,...b->...a", U[i].conj(), psi), i, -1)
        psi = (psi + alpha * h) / (1.0 + 2 * len(dirs) * alpha)
    return psi


def wuppertal_cols(U3, psi, alpha, n_iter):
    """Fast spatial Wuppertal smearing on a subset of timeslices.
    U3: spatial links restricted to the timeslices, [3, nt, z, y, x, 3, 3];
    psi: [nt, z, y, x, ..., 3] with colour LAST and any number of extra (spin / column) axes.
    Same operator as `wuppertal(..., spatial_only=True)`; batched matmul, all columns at once."""
    xp = get_xp(psi)
    shp = psi.shape
    nt, Lz, Ly, Lx = shp[:4]
    P = psi.reshape(nt, Lz, Ly, Lx, -1, 3)
    Uf = [U3[i] for i in range(3)]
    Ub = [shift(U3[i], i, -1).conj().swapaxes(-1, -2) for i in range(3)]  # U_i^dag(x - i)
    for _ in range(n_iter):
        h = 0
        for i in range(3):
            # U_i(x) psi(x+i):  [.., k, 3] @ U^T  ->  sum_b U_ab psi_kb
            h = h + xp.matmul(shift(P, i, 1), Uf[i].swapaxes(-1, -2))
            h = h + xp.matmul(shift(P, i, -1), Ub[i].swapaxes(-1, -2))
        P = (P + alpha * h) / (1.0 + 6 * alpha)
    return P.reshape(shp)
