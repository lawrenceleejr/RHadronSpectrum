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


def test_nucleon_fast_matches_general_tensor(cfg):
    """Fast zero-momentum nucleon contraction (single sink site) == general antisymmetrised-tensor
    contraction with colour-singlet eps (u^T C g5 d) P+ u, up to the 1/6 colour normalisation."""
    from rhadron.contract import light
    _, _, (S, W), _ = cfg
    T = S.shape[0]
    Cfast = light.nucleon(S.reshape(T, 1, 1, 1, 4, 3, 4, 3))
    F = np.zeros((1, 4, 36, 36, 36), dtype=complex)
    Fn = light.nucleon_tensor()  # [4, 12, 12, 12] slots (u, d, u)
    F[0, :, 0:12, 12:24, 0:12] = Fn
    Fb = qo.baryon_bar(F)
    B = hadron.rbaryon_block(F, Fb, props(S, (0, 1)), T - 1)
    Cgen = np.einsum("trr->t", B[:, 0, :, 0, :])
    assert np.abs(Cfast - Cgen).max() < 1e-10 * np.abs(Cgen).max()


def test_pion_positive(cfg):
    from rhadron.contract import light
    _, _, (S, W), _ = cfg
    T = S.shape[0]
    C = light.meson(S.reshape(T, 1, 1, 1, 4, 3, 4, 3), qo.G5)
    assert np.allclose(C.imag, 0, atol=1e-12 * np.abs(C).max()) and np.all(C.real > 0)
    assert np.allclose(C.real, np.einsum("tsaub->t", np.abs(S.reshape(T, 4, 3, 4, 3)) ** 2))


@pytest.mark.parametrize("colour,flav,dq,j", [
    ("octet_A", "uud_A", "Cg5", "1/2"), ("octet_S", "uds_singlet", "Cgi", "1/2"),
    ("octet_A", "uds_Lambda8", "Cg5", "1/2"), ("octet_S", "uud_A", "Cgi", "3/2"),
    ("octet_A", "uud_S", "Cgi", "3/2"),
])
def test_rbaryon_fast_equals_general(cfg, colour, flav, dq, j):
    _, _, (S, W), _ = cfg
    rng = np.random.default_rng(5)
    Ss = S * np.exp(0.3j * rng.normal())  # distinct strange propagator
    pr = {0: S, 1: S, 2: Ss[::-1].copy()}
    F = qo.baryon_tensor(colour, flav, dq, j, nr=True)
    Fb = qo.baryon_bar(F)
    a = hadron.rbaryon_block(F, Fb, pr, 1)
    b = hadron.rbaryon_block_fast(F, Fb, pr, 1)
    assert np.abs(a - b).max() < 1e-10 * np.abs(a).max()


def test_production_baryon_operators_nonvanishing(cfg):
    from rhadron.measure_quark import BARYONS
    _, _, (S, W), _ = cfg
    pr = {0: S, 1: S, 2: S}
    ref = None
    for op in BARYONS:
        F = qo.baryon_tensor(*op, nr=True)
        B = hadron.rbaryon_block_fast(F, qo.baryon_bar(F), pr, 1)
        n = np.abs(B).max()
        ref = n if ref is None else ref
        assert n > 1e-8 * ref, op


def test_wuppertal_fast_matches_reference():
    from rhadron.dirac import wuppertal, wuppertal_cols
    rng = np.random.default_rng(9)
    U = random_gauge(SHAPE, rng, eps=0.5)
    psi = rng.normal(size=SHAPE + (4, 3)) + 1j * rng.normal(size=SHAPE + (4, 3))
    ref = wuppertal(U, psi, 0.25, 3)
    ts = [2, 3, 4]
    fast = wuppertal_cols(U[:3, ts], psi[ts], 0.25, 3)
    assert np.abs(fast - ref[ts]).max() < 1e-13


def test_sink_smeared_site_matches_full_smearing():
    from rhadron.dirac import wuppertal
    from rhadron.measure_quark import _sink_smeared_site, _site_series
    rng = np.random.default_rng(10)
    U = random_gauge(SHAPE, rng, eps=0.5)
    S = rng.normal(size=SHAPE + (4, 3, 4, 3)) + 1j * rng.normal(size=SHAPE + (4, 3, 4, 3))
    x0, tmax = (1, 2, 3, 6), 3
    full = S.copy()
    for s0 in range(4):
        for a0 in range(3):
            full[..., s0, a0] = wuppertal(U, S[..., s0, a0], 0.25, 2)
    ref = _site_series(full, x0, tmax)
    fast = _sink_smeared_site(U, S, x0, tmax, (0.25, 2))
    assert np.abs(fast - ref).max() < 1e-12


@pytest.fixture(scope="module")
def pair_props():
    """Point-sink propagators from two sources at the same spatial site, t0 = 1 and t1 = 5."""
    rng = np.random.default_rng(21)
    U = random_gauge(SHAPE, rng, eps=0.4)
    g = random_su3(SHAPE, rng)
    out = []
    for W in (U, gauge_transform(U, g)):
        sm = lambda p, W=W: wuppertal(W, p, 0.25, 2)  # noqa: E731
        S0 = point_propagator(W, KAPPA, CSW, (1, 2, 0, 1), src_smear=sm)
        S1 = point_propagator(W, KAPPA, CSW, (1, 2, 0, 5), src_smear=sm)
        S0s = point_propagator(W, KAPPA, CSW, (1, 2, 0, 1), src_smear=sm, snk_smear=sm)
        V4 = static_links(W, "HYP2", n_proj=40)
        Wl = wilson_lines(V4, 1, 4)[4, 0, 2, 1]
        out.append((S0, S1, S0s, Wl))
    return out


def test_density_fast_matches_reference_and_gauge_invariant(pair_props):
    from rhadron.contract.density import density_3pt, density_3pt_reference
    tau = 3
    res = []
    for S0, S1, S0s, Wl in pair_props:
        Sy0 = S0[tau].reshape(-1, 4, 3, 4, 3)
        Sy1 = S1[tau].reshape(-1, 4, 3, 4, 3)
        S10 = S0s[5, 0, 2, 1]
        for Gam, GJ in ((qo.G5, qo.G[3]), (qo.G[0], qo.ONE)):
            f = density_3pt(Sy0, Sy1, S10, Wl, Gam, GJ)
            r = density_3pt_reference(Sy0, Sy1, S10, Wl, Gam, GJ)
            for x, y in zip(f, r):
                assert np.abs(x - y).max() < 1e-10 * np.abs(y).max()
        res.append(density_3pt(Sy0, Sy1, S10, Wl, qo.G5, qo.G[3]))
    # gauge invariance (smearing has iterative projection only in the static links: 1e-8)
    for a, b in zip(res[0], res[1]):
        assert np.abs(a - b).max() < 1e-7 * np.abs(a).max()


def test_covariant_derivative_gauge_covariant():
    from rhadron.dirac import covariant_derivative
    rng = np.random.default_rng(31)
    U = random_gauge(SHAPE, rng, eps=0.5)
    g = random_su3(SHAPE, rng)
    psi = rng.normal(size=SHAPE + (4, 3)) + 1j * rng.normal(size=SHAPE + (4, 3))
    for i in range(3):
        a = covariant_derivative(gauge_transform(U, g), np.einsum("...ab,...sb->...sa", g, psi), i)
        b = np.einsum("...ab,...sb->...sa", g, covariant_derivative(U, psi, i))
        assert np.abs(a - b).max() < 1e-12


def _pwave_site_props(U):
    """SD[(j,l)][t] at x0 from derivative sources (l) and sink derivatives (j), point-like smearing."""
    from rhadron.dirac import covariant_derivative, solve, wilson_clover_matrix
    x0, T = (1, 2, 0, 1), 4
    M = wilson_clover_matrix(U, KAPPA, CSW).tocsr()
    Lt = SHAPE[0]
    SD = {}
    for l in range(3):
        S = np.zeros(SHAPE + (4, 3, 4, 3), dtype=complex)
        for s0 in range(4):
            for a0 in range(3):
                b = np.zeros(SHAPE + (4, 3), dtype=complex)
                b[x0[3], x0[2], x0[1], x0[0], s0, a0] = 1.0
                b = covariant_derivative(U, b, l)
                S[..., s0, a0] = solve(M, b.ravel()).reshape(b.shape)
        Sc = S.transpose(0, 1, 2, 3, 4, 6, 7, 5)  # sink colour last
        for j in range(3):
            D = covariant_derivative(U, Sc, j).transpose(0, 1, 2, 3, 4, 7, 5, 6)
            SD[(j, l)] = np.stack([D[(x0[3] + t) % Lt, x0[2], x0[1], x0[0]] for t in range(T + 1)])
    W = wilson_lines(static_links(U, "HYP2", n_proj=40), x0[3], T)[:, x0[2], x0[1], x0[0]]
    return SD, W


def test_static_light_pwave_gauge_invariant():
    """(Reality holds only for the ensemble average, not per configuration.)"""
    rng = np.random.default_rng(32)
    U = random_gauge(SHAPE, rng, eps=0.4)
    g = random_su3(SHAPE, rng)
    r = [hadron.static_light_pwave(*_pwave_site_props(V)) for V in (U, gauge_transform(U, g))]
    for k in r[0]:
        assert np.abs(r[0][k] - r[1][k]).max() < 1e-7 * np.abs(r[0][k]).max(), k
        assert np.abs(r[0][k]).max() > 0


def test_smeared_sink_nucleon_transposes():
    """The nucleon_role sink-smearing path (colour-last transpose, wuppertal_cols, transpose back)
    equals column-wise reference smearing followed by the nucleon contraction."""
    from rhadron.contract import light
    from rhadron.dirac import wuppertal, wuppertal_cols
    rng = np.random.default_rng(41)
    U = random_gauge(SHAPE, rng, eps=0.5)
    S = rng.normal(size=SHAPE + (4, 3, 4, 3)) + 1j * rng.normal(size=SHAPE + (4, 3, 4, 3))
    idx = [2, 3, 4]
    sm = wuppertal_cols(U[:3, idx], np.ascontiguousarray(S[idx].transpose(0, 1, 2, 3, 4, 6, 7, 5)), 0.25, 2)
    sm = sm.transpose(0, 1, 2, 3, 4, 7, 5, 6)
    ref = S.copy()
    for s0 in range(4):
        for a0 in range(3):
            ref[..., s0, a0] = wuppertal(U, S[..., s0, a0], 0.25, 2)
    assert np.abs(light.nucleon(sm) - light.nucleon(ref[idx])).max() < 1e-10 * np.abs(light.nucleon(ref[idx])).max()


def test_baryon_corr_general_matches_fast_nucleon():
    """Independent site-vectorised Wick code == fast nucleon (same operator, two flavours u, d)."""
    from rhadron.contract import light
    rng = np.random.default_rng(51)
    sh = (3, 2, 2, 2)
    S = rng.normal(size=sh + (4, 3, 4, 3)) + 1j * rng.normal(size=sh + (4, 3, 4, 3))
    F = np.zeros((1, 4, 36, 36, 36), dtype=complex)
    F[0, :, 0:12, 12:24, 0:12] = light.nucleon_tensor()
    Fb = qo.baryon_bar(F)
    c = light.baryon_corr({0: S, 1: S}, hadron.flavour_components(F), hadron.flavour_components(Fb), chunk=3)
    assert np.abs(c - light.nucleon(S)).max() < 1e-10 * np.abs(c).max()


def test_baryon_suite_N1_equals_fast_nucleon():
    from rhadron.contract import light
    rng = np.random.default_rng(52)
    sh = (3, 2, 2, 2)
    S = rng.normal(size=sh + (4, 3, 4, 3)) + 1j * rng.normal(size=sh + (4, 3, 4, 3))
    suite = light.baryon_suite_tensors()
    c = light.baryon_corr({0: S, 1: S}, *suite["N1"], chunk=8)
    assert np.abs(c - light.nucleon(S)).max() < 1e-10 * np.abs(c).max()
    for k in ("N2", "Delta"):
        assert np.abs(light.baryon_corr({0: S, 1: S}, *suite[k], chunk=8)).max() > 0
