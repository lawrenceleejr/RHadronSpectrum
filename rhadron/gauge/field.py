"""SU(3) gauge fields on a periodic 4D lattice.

Layout: ``U[mu, t, z, y, x, a, b]`` (complex128), ``mu = 0, 1, 2, 3 = x, y, z, t`` (QUDA ordering
of directions, PyQUDA lexicographic site order).  Site fields are ``[t, z, y, x, ...]``.
``U[mu](n)`` is the link from ``n`` to ``n + mu``.
"""
import numpy as np

from ..backend import get_xp

NC = 3
ND = 4
# array axis of direction mu inside a site field [t, z, y, x, ...]
SITE_AXIS = {0: 3, 1: 2, 2: 1, 3: 0}


def shift(f, mu, s):
    """Return g(n) = f(n + s*mu) for a site field f[t,z,y,x,...] (periodic)."""
    xp = get_xp(f)
    return xp.roll(f, -s, axis=SITE_AXIS[mu])


def dag(m):
    return m.conj().swapaxes(-1, -2)


def mul(a, b):
    xp = get_xp(a)
    return xp.matmul(a, b)


def trace(m):
    return m[..., 0, 0] + m[..., 1, 1] + m[..., 2, 2]


def lattice_shape(U):
    return U.shape[1:5]  # (Lt, Lz, Ly, Lx)


def unit_gauge(shape, xp=np):
    Lt, Lz, Ly, Lx = shape
    U = xp.zeros((ND, Lt, Lz, Ly, Lx, NC, NC), dtype=complex)
    U[..., 0, 0] = U[..., 1, 1] = U[..., 2, 2] = 1.0
    return U


def random_su3(shape, rng, xp=np, eps=None):
    """Random SU(3) matrices.  eps=None: Haar; otherwise close to identity (exp(i eps H))."""
    if eps is None:
        z = rng.normal(size=shape + (NC, NC)) + 1j * rng.normal(size=shape + (NC, NC))
        q, r = np.linalg.qr(z)
        d = np.diagonal(r, axis1=-2, axis2=-1)
        q = q * (d / np.abs(d))[..., None, :]
        det = np.linalg.det(q)
        q = q / (det ** (1.0 / 3.0))[..., None, None]
    else:
        h = rng.normal(size=shape + (NC, NC)) + 1j * rng.normal(size=shape + (NC, NC))
        h = 0.5 * (h + h.conj().swapaxes(-1, -2))
        h -= np.trace(h, axis1=-2, axis2=-1)[..., None, None] * np.eye(NC) / NC
        w, v = np.linalg.eigh(h)
        q = (v * np.exp(1j * eps * w)[..., None, :]) @ v.conj().swapaxes(-1, -2)
    return xp.asarray(q)


def random_gauge(shape, rng, xp=np, eps=None):
    return random_su3((ND,) + tuple(shape), rng, xp=xp, eps=eps)


def gauge_transform(U, g):
    """U'_mu(n) = g(n) U_mu(n) g(n+mu)^dagger."""
    xp = get_xp(U)
    out = xp.empty_like(U)
    for mu in range(ND):
        out[mu] = mul(mul(g, U[mu]), dag(shift(g, mu, +1)))
    return out


def plaquette_field(U, mu, nu):
    """P_{mu nu}(n) = U_mu(n) U_nu(n+mu) U_mu(n+nu)^dag U_nu(n)^dag."""
    return mul(mul(U[mu], shift(U[nu], mu, 1)), mul(dag(shift(U[mu], nu, 1)), dag(U[nu])))


def plaquette(U):
    """Average plaquette (1/3) Re Tr P, averaged over 6 planes; also spatial and temporal parts."""
    xp = get_xp(U)
    ps, pt = [], []
    for mu in range(ND):
        for nu in range(mu + 1, ND):
            p = float(xp.mean(trace(plaquette_field(U, mu, nu)).real)) / NC
            (pt if nu == 3 else ps).append(p)
    return (sum(ps) + sum(pt)) / 6.0, sum(ps) / 3.0, sum(pt) / 3.0


def reunitarize(m):
    """Project a near-SU(3) matrix back to SU(3) (Gram-Schmidt rows 1,2; row 3 = (r1 x r2)*)."""
    xp = get_xp(m)
    r0 = m[..., 0, :]
    r0 = r0 / xp.sqrt(xp.sum(xp.abs(r0) ** 2, axis=-1, keepdims=True))
    r1 = m[..., 1, :]
    r1 = r1 - xp.sum(r0.conj() * r1, axis=-1, keepdims=True) * r0
    r1 = r1 / xp.sqrt(xp.sum(xp.abs(r1) ** 2, axis=-1, keepdims=True))
    r2 = xp.cross(r0, r1).conj()
    return xp.stack([r0, r1, r2], axis=-2)


def project_su3(m, n_iter=10):
    """Projection onto SU(3): the V maximising Re Tr(V^dag m), via iterated Cabibbo-Marinari SU(2)
    subgroup maximisation starting from the Gram-Schmidt unitarisation.  Deterministic."""
    xp = get_xp(m)
    v = reunitarize(m)
    for _ in range(n_iter):
        for (i, j) in ((0, 1), (1, 2), (0, 2)):
            w = mul(m, dag(v))  # V' = S V  =>  maximise Re Tr(S^dag W)
            al = 0.5 * (w[..., i, i] + w[..., j, j].conj())
            be = 0.5 * (w[..., i, j] - w[..., j, i].conj())
            k = xp.sqrt(xp.abs(al) ** 2 + xp.abs(be) ** 2)
            k = xp.where(k == 0, 1.0, k)
            al, be = al / k, be / k
            s = xp.zeros_like(m)
            s[..., 0, 0] = s[..., 1, 1] = s[..., 2, 2] = 1.0
            s[..., i, i] = al
            s[..., i, j] = be
            s[..., j, i] = -be.conj()
            s[..., j, j] = al.conj()
            v = mul(s, v)
    return v
