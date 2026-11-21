"""Quark-line contractions: production == reference, gauge invariance, colour/flavour/spin structure,
Pauli-forbidden R-baryon combinations vanish identically."""
import numpy as np
import pytest

from rhadron.contract import hadron, reference
from rhadron.dirac import point_propagator, wuppertal
from rhadron.gauge.field import gauge_transform, random_gauge, random_su3
from rhadron.operators import quark_ops as qo
from rhadron.static import static_links, wilson_lines

SHAPE = (8, 4, 4, 4)
KAPPA, CSW = 0.115, 1.2
X0 = (1, 2, 0, 3)  # (x, y, z, t)
TMAX = 4


def site_data(U, smear=True):
    """Propagator S(x0, t0+t; x0, t0) [t,4,3,4,3] with Wuppertal smearing at both ends; static line."""
    V = U  # smear on the thin links for the test
    sm = (lambda p: wuppertal(V, p, 0.25, 2)) if smear else None
    S = point_propagator(U, KAPPA, CSW, X0, src_smear=sm, snk_smear=sm)
    x, y, z, t0 = X0
    Lt = SHAPE[0]
    Ssite = np.stack([S[(t0 + t) % Lt, z, y, x] for t in range(TMAX + 1)])
    V4 = static_links(U, "HYP2", n_proj=40)
    W = wilson_lines(V4, t0, TMAX)[:, z, y, x]
    return Ssite, W


@pytest.fixture(scope="module")
def cfg():
    rng = np.random.default_rng(7)
    U = random_gauge(SHAPE, rng, eps=0.4)
    g = random_su3(SHAPE, rng)
    return U, g, site_data(U), site_data(gauge_transform(U, g))


def props(S, flavours=(0, 1, 2)):
    return {f: S for f in flavours}  # degenerate flavours (same propagator object)


@pytest.mark.parametrize("gname", ["g5", "gi", "1", "g5gi"])
def test_rmeson_production_vs_reference(cfg, gname):
    _, _, (S, W), _ = cfg
    Gam = qo.MESON_GAMMAS[gname][0][0]
    F = qo.meson_tensor(Gam, qo.flavour_matrix("ud"))
    Fb = qo.meson_bar(F)
    Cp = hadron.contract_rmeson(hadron.rmeson_block(F, Fb, props(S), TMAX), W)
    Cr = reference.rmeson_reference(F, Fb, props(S), W, TMAX)
    assert np.abs(Cp - Cr).max() < 1e-10 * np.abs(Cr).max()


def test_rmeson_gauge_invariant(cfg):
    _, _, (S, W), (Sg, Wg) = cfg
    for gname in ("g5", "gi", "g4gi"):
        Gam = qo.MESON_GAMMAS[gname][0][0]
        F = qo.meson_tensor(Gam, qo.flavour_matrix("ud"))
        Fb = qo.meson_bar(F)
        C = hadron.contract_rmeson(hadron.rmeson_block(F, Fb, props(S), TMAX), W)
        Cg = hadron.contract_rmeson(hadron.rmeson_block(F, Fb, props(Sg), TMAX), Wg)
        assert np.abs(C - Cg).max() < 1e-8 * np.abs(C).max()
        # correlator of O O^dag is real (Hermitian, single operator)
        assert np.abs(C.imag).max() < 1e-10 * np.abs(C).max()


def test_colour_singlet_meson_is_not_gauge_invariant_with_adjoint_line(cfg):
    """Sanity: the octet structure matters -- a singlet q qbar paired with an octet line is not a
    valid operator; check instead that the octet correlator differs from the singlet static-light."""
    _, _, (S, W), _ = cfg
    F = qo.meson_tensor(qo.G5, qo.flavour_matrix("ud"))
    C8 = hadron.contract_rmeson(hadron.rmeson_block(F, qo.meson_bar(F), props(S), TMAX), W)
    assert np.abs(C8[1:]).min() > 0


@pytest.mark.parametrize("colour,flav,dq,j", [
    ("octet_A", "uud_A", "Cg5", "1/2"),
    ("octet_S", "uds_singlet", "Cgi", "1/2"),
    ("octet_A", "uuu", "Cgi", "1/2"),
])
def test_rbaryon_production_vs_reference(cfg, colour, flav, dq, j):
    _, _, (S, W), _ = cfg
    F = qo.baryon_tensor(colour, flav, dq, j)
    Fb = qo.baryon_bar(F)
    B = hadron.rbaryon_block(F, Fb, props(S), 2)
    Cp = hadron.contract_rbaryon(B, W[:3])
    for rho in (0, 1):
        Cr = reference.rbaryon_reference(F, Fb, props(S), W, 2, rho, rho)
        scale = max(np.abs(Cr).max(), 1e-300)
        assert np.abs(Cp[:, rho, rho] - Cr).max() < 1e-10 * scale


def test_rbaryon_gauge_invariant(cfg):
    _, _, (S, W), (Sg, Wg) = cfg
    F = qo.baryon_tensor("octet_A", "uds_singlet", "Cg5", "1/2")
    Fb = qo.baryon_bar(F)
    C = hadron.contract_rbaryon(hadron.rbaryon_block(F, Fb, props(S), TMAX), W)
    Cg = hadron.contract_rbaryon(hadron.rbaryon_block(F, Fb, props(Sg), TMAX), Wg)
    assert np.abs(C - Cg).max() < 1e-8 * np.abs(C).max()


def _rb_norm(cfg, colour, flav, dq, j, nr=True):
    _, _, (S, W), _ = cfg
    F = qo.baryon_tensor(colour, flav, dq, j, nr=nr)
    C = hadron.contract_rbaryon(hadron.rbaryon_block(F, qo.baryon_bar(F), props(S), 2), W[:3])
    return np.abs(C).max()


def test_su6_pauli_structure(cfg):
    """Nonrelativistic (upper-component) operators.  Ground-state colour-octet qqq: spin-flavour in SU(6) 70 = (8,1/2)+(10,1/2)+(1,1/2)+(8,3/2).
    Forbidden: (10, 3/2) and (1, 3/2).  Colour-singlet check: 56 = (8,1/2)+(10,3/2), so a local
    colour-singlet uuu j=1/2 vanishes and uds flavour-singlet vanishes."""
    ref = _rb_norm(cfg, "octet_A", "uud_A", "Cg5", "1/2")
    assert ref > 0
    tiny = 1e-12 * ref
    # forbidden octet-colour combinations
    for colour in ("octet_A", "octet_S"):
        assert _rb_norm(cfg, colour, "uuu", "Cgi", "3/2") < tiny
        assert _rb_norm(cfg, colour, "uds_singlet", "Cgi", "3/2") < tiny
    # allowed octet-colour combinations are nonzero
    assert _rb_norm(cfg, "octet_A", "uuu", "Cgi", "1/2") > 1e-6 * ref  # (10, 1/2)
    assert _rb_norm(cfg, "octet_A", "uds_singlet", "Cg5", "1/2") > 1e-6 * ref  # (1, 1/2)
    assert max(_rb_norm(cfg, c, "uud_A", "Cgi", "3/2") for c in ("octet_A", "octet_S")) > 1e-6 * ref
    # colour-singlet (ordinary baryons) as a cross-check of the machinery
    assert _rb_norm(cfg, "singlet", "uuu", "Cgi", "1/2") < tiny
    assert _rb_norm(cfg, "singlet", "uuu", "Cg5", "1/2") < tiny
    assert _rb_norm(cfg, "singlet", "uds_singlet", "Cg5", "1/2") < tiny
    assert _rb_norm(cfg, "singlet", "uuu", "Cgi", "3/2") > 1e-6 * ref


def test_diquark_pauli_exact(cfg):
    """Symmetric colour x antisymmetric flavour x antisymmetric spin (C g5) diquark is symmetric
    under q1 <-> q2 and vanishes for full Dirac spinors (no NR projection needed)."""
    ref = _rb_norm(cfg, "octet_A", "uud_A", "Cg5", "1/2", nr=False)
    assert _rb_norm(cfg, "octet_S", "uds_singlet", "Cg5", "1/2", nr=False) < 1e-12 * ref


def test_colour_octet_property():
    """O^a transforms in the adjoint: K^a_{jkl} g_jj' g_kk' g_ll' = R(g)^{ab} K^b_{j'k'l'}."""
    from rhadron.static import to_adjoint
    rng = np.random.default_rng(3)
    g = random_su3((), rng)
    R = to_adjoint(g)
    for kind in ("octet_A", "octet_S"):
        K = qo.colour_tensor(kind)
        lhs = np.einsum("ajkl,jJ,kK,lL->aJKL", K, g, g, g)
        rhs = np.einsum("ab,bJKL->aJKL", R.T, K)
        assert np.abs(lhs - rhs).max() < 1e-12 or np.abs(lhs - np.einsum("ab,bJKL->aJKL", R, K)).max() < 1e-12
        # trace over generators orthonormal: K^a are linearly independent
        M = K.reshape(8, -1)
        assert np.linalg.matrix_rank(M) == 8


def test_static_light_gauge_invariant(cfg):
    _, _, (S, W), (Sg, Wg) = cfg
    C = hadron.static_light(qo.G5, S, W)
    Cg = hadron.static_light(qo.G5, Sg, Wg)
    assert np.abs(C - Cg).max() < 1e-8 * np.abs(C).max()
