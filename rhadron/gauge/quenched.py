"""Quenched SU(3) generation for the Wilson plaquette action S = beta sum_P (1 - Re Tr U_P / 3):
Cabibbo-Marinari pseudo-heatbath (Kennedy-Pendleton SU(2) heatbath) + SU(2) over-relaxation,
vectorised over checkerboard parity (links of one direction and parity are mutually independent).
Runs on NumPy or CuPy arrays."""
import numpy as np

from ..backend import get_xp
from .field import ND, dag, mul, reunitarize, shift

SUBGROUPS = ((0, 1), (1, 2), (0, 2))


def staple_sum(U, mu):
    """A_mu(n) with S_link = -(beta/3) Re Tr[U_mu(n) A_mu(n)]."""
    A = 0
    for nu in range(ND):
        if nu == mu:
            continue
        Unu_pmu = shift(U[nu], mu, 1)
        A = A + mul(mul(Unu_pmu, dag(shift(U[mu], nu, 1))), dag(U[nu]))
        Unu_m = shift(U[nu], nu, -1)
        A = A + mul(mul(dag(shift(Unu_m, mu, 1)), dag(shift(U[mu], nu, -1))), Unu_m)
    return A


def parity_mask(shape, p, xp=np):
    t, z, y, x = np.indices(shape)
    return xp.asarray(((t + z + y + x) % 2) == p)


def _su2_from_sub(W, i, j):
    xp = get_xp(W)
    al = 0.5 * (W[..., i, i] + W[..., j, j].conj())
    be = 0.5 * (W[..., i, j] - W[..., j, i].conj())
    k = xp.sqrt(xp.abs(al) ** 2 + xp.abs(be) ** 2)
    ks = xp.where(k == 0, 1.0, k)
    return al / ks, be / ks, k


def _embed(al, be, i, j, like):
    """3x3 matrix embedding the SU(2) element [[al, be], [-be*, al*]] into rows/cols (i, j)."""
    xp = get_xp(like)
    R = xp.zeros(al.shape + (3, 3), dtype=like.dtype)
    R[..., 0, 0] = R[..., 1, 1] = R[..., 2, 2] = 1.0
    R[..., i, i] = al
    R[..., i, j] = be
    R[..., j, i] = -be.conj()
    R[..., j, j] = al.conj()
    return R


def _kp_x0(a, rng, xp):
    """Kennedy-Pendleton: sample x0 with density ~ sqrt(1-x0^2) exp(a x0), a > 0 (vectorised)."""
    x0 = xp.zeros(a.shape)
    todo = xp.ones(a.shape, dtype=bool)
    while bool(todo.any()):
        n = a.shape
        r1 = 1.0 - rng.random(n)
        r2 = rng.random(n)
        r3 = 1.0 - rng.random(n)
        r4 = rng.random(n)
        lam2 = -(xp.log(r1) + xp.cos(2 * np.pi * r2) ** 2 * xp.log(r3)) / (2.0 * a)
        acc = todo & (r4 ** 2 <= 1.0 - lam2)
        x0 = xp.where(acc, 1.0 - 2.0 * lam2, x0)
        todo = todo & ~acc
    return x0


def _random_su2(x0, rng, xp):
    n = x0.shape
    r = xp.sqrt(xp.clip(1.0 - x0 ** 2, 0.0, None))
    cth = 2.0 * rng.random(n) - 1.0
    phi = 2.0 * np.pi * rng.random(n)
    sth = xp.sqrt(1.0 - cth ** 2)
    x1, x2, x3 = r * sth * xp.cos(phi), r * sth * xp.sin(phi), r * cth
    # x = x0 + i x.sigma  ->  [[x0 + i x3, x2 + i x1], [-x2 + i x1, x0 - i x3]]
    return x0 + 1j * x3, x2 + 1j * x1


def _rows_update(M, ra, rb, i, j):
    """M <- R M with R the SU(2) element [[ra, rb], [-rb*, ra*]] embedded in rows (i, j)."""
    Mi, Mj = M[..., i, :], M[..., j, :]
    ni = ra[..., None] * Mi + rb[..., None] * Mj
    nj = -rb.conj()[..., None] * Mi + ra.conj()[..., None] * Mj
    M[..., i, :] = ni
    M[..., j, :] = nj


def update_links(U, mu, p, beta, rng, mode, mask=None):
    """One heatbath ('hb') or over-relaxation ('or') update of links U[mu] on parity p (in place)."""
    xp = get_xp(U)
    shape = U.shape[1:5]
    mask = parity_mask(shape, p, xp) if mask is None else mask
    A = staple_sum(U, mu)[mask]
    Ul = U[mu][mask]
    W = mul(Ul, A)  # updated alongside Ul:  (R U) A = R W
    for (i, j) in SUBGROUPS:
        al, be, k = _su2_from_sub(W, i, j)  # v = [[al, be], [-be*, al*]]
        if mode == "hb":
            a = (2.0 * beta / 3.0) * k
            x0 = _kp_x0(xp.maximum(a, 1e-12), rng, xp)
            xa, xb = _random_su2(x0, rng, xp)
            # r = x v^dag ; v^dag = [[al*, -be], [be*, al]]
            ra = xa * al.conj() + xb * be.conj()
            rb = -xa * be + xb * al
        else:  # over-relaxation r = (v^dag)^2
            ra = al.conj() ** 2 - be * be.conj()
            rb = -al.conj() * be - be * al
        _rows_update(Ul, ra, rb, i, j)
        _rows_update(W, ra, rb, i, j)
    U[mu][mask] = reunitarize(Ul)
    return U


def sweep(U, beta, rng, n_or=4):
    """One compound sweep: 1 heatbath + n_or over-relaxation sweeps over all links."""
    xp = get_xp(U)
    shape = U.shape[1:5]
    masks = [parity_mask(shape, p, xp) for p in (0, 1)]
    for mode in ["hb"] + ["or"] * n_or:
        for mu in range(ND):
            for p in (0, 1):
                update_links(U, mu, p, beta, rng, mode, masks[p])
    return U
