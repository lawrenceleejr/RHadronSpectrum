"""Link smearing: spatial APE, spatial stout, 4D HYP (for static-line temporal links)."""
from functools import lru_cache

from ..backend import get_xp
from .field import ND, dag, mul, project_su3, shift

SPATIAL = (0, 1, 2)
T = 3


def staple(U, mu, nu, Umu=None):
    """Sum of the two staples of link mu in the (mu, nu) plane.  U may be a dict/list of link fields;
    Umu (default U[mu]) is the link transported along the staple's far side."""
    Umu = U[mu] if Umu is None else Umu
    Unu = U[nu]
    up = mul(mul(Unu, shift(Umu, nu, 1)), dag(shift(Unu, mu, 1)))
    Unu_m = shift(Unu, nu, -1)
    dn = mul(mul(dag(Unu_m), shift(Umu, nu, -1)), shift(Unu_m, mu, 1))
    return up + dn


def ape_spatial(U, alpha, n_iter, n_proj=10):
    """Spatial APE: U_i <- Proj[(1-alpha) U_i + alpha/4 sum_{j != i, spatial} staples].  Temporal
    links untouched.  Returns a new array."""
    xp = get_xp(U)
    V = U.copy()
    for _ in range(n_iter):
        new = V.copy()
        for i in SPATIAL:
            s = sum(staple(V, i, j) for j in SPATIAL if j != i)
            new[i] = project_su3((1.0 - alpha) * V[i] + (alpha / 4.0) * s, n_proj)
        V = new
    return V


def _expi_traceless_hermitian(Q):
    """exp(i Q) for traceless Hermitian 3x3 Q via eigen-decomposition."""
    xp = get_xp(Q)
    w, v = xp.linalg.eigh(Q)
    return mul(v * xp.exp(1j * w)[..., None, :], dag(v))


def stout_spatial(U, rho, n_iter):
    """Spatial stout smearing (Morningstar-Peardon) with isotropic rho in the 3 spatial directions."""
    xp = get_xp(U)
    V = U.copy()
    eye = xp.eye(3)
    for _ in range(n_iter):
        new = V.copy()
        for i in SPATIAL:
            C = rho * sum(staple(V, i, j) for j in SPATIAL if j != i)
            Om = mul(C, dag(V[i]))
            A = 0.5 * (dag(Om) - Om)
            Q = 1j * (A - (A[..., 0, 0] + A[..., 1, 1] + A[..., 2, 2])[..., None, None] * eye / 3.0)
            new[i] = mul(_expi_traceless_hermitian(Q), V[i])
        V = new
    return V


HYP_PARAMS = {"HYP1": (0.75, 0.6, 0.3), "HYP2": (1.0, 1.0, 0.5)}


def hyp_links(U, alphas, dirs=(T,), n_proj=10):
    """HYP-smeared links (Hasenfratz-Knechtli) for the directions in ``dirs`` (default: temporal only,
    as needed for the static line).  alphas = (alpha1, alpha2, alpha3).  Returns dict mu -> field."""
    a1, a2, a3 = alphas

    def proj(m):
        return project_su3(m, n_proj)

    @lru_cache(maxsize=None)
    def vbar(mu, excl):  # level 1: decorated link mu, staples orthogonal to mu and to excl (2 dirs)
        others = [r for r in range(ND) if r != mu and r not in excl]
        s = sum(staple(U, mu, r) for r in others)
        return proj((1 - a3) * U[mu] + (a3 / 2.0) * s)

    @lru_cache(maxsize=None)
    def vtil(mu, nu):  # level 2: link mu, staples in directions rho != mu, nu built from vbar
        s = 0
        for r in range(ND):
            if r in (mu, nu):
                continue
            ex = tuple(sorted((nu, mu)))
            Lr = {r: vbar(r, ex), mu: vbar(mu, tuple(sorted((r, nu))))}
            s = s + staple(Lr, mu, r)
        return proj((1 - a2) * U[mu] + (a2 / 4.0) * s)

    out = {}
    for mu in dirs:
        s = 0
        for r in range(ND):
            if r == mu:
                continue
            Lr = {r: vtil(r, mu), mu: vtil(mu, r)}
            s = s + staple(Lr, mu, r)
        out[mu] = proj((1 - a1) * U[mu] + (a1 / 6.0) * s)
    return out
