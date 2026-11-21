import numpy as np
import pytest

from rhadron.groups.oh import IRREPS, character, dim, elements, mult_table, projector, rep
from rhadron.operators.paths import SHAPES, orbit, rep_matrices

G = elements()


@pytest.mark.parametrize("ir", IRREPS)
def test_irrep_homomorphism_and_orthogonality(ir):
    mt = mult_table()
    for i in range(48):
        for j in range(48):
            assert np.abs(rep(ir, G[i]) @ rep(ir, G[j]) - rep(ir, G[mt[i, j]])).max() < 1e-12
        D = rep(ir, G[i])
        assert np.allclose(D @ D.T, np.eye(dim(ir)))


def test_character_orthonormality():
    X = np.array([[character(a, g) for g in G] for a in IRREPS])
    assert np.allclose(X @ X.T / 48, np.eye(10))


@pytest.mark.parametrize("shape", list(SHAPES))
@pytest.mark.parametrize("cs", [-1, 1])
def test_projectors_on_orbits(shape, cs):
    keys, act = orbit(SHAPES[shape])
    n = len(keys)
    T = rep_matrices(act, n, cs)
    total = np.zeros((n, n))
    Ps = {}
    for ir in IRREPS:
        for lam in range(dim(ir)):
            P = projector(ir, T, lam)
            assert np.allclose(P @ P, P, atol=1e-12)  # idempotent
            Ps[(ir, lam)] = P
            total += P
    assert np.allclose(total, np.eye(n), atol=1e-12)  # complete
    ks = list(Ps)
    for a in ks:
        for b in ks:
            if a != b:
                assert np.allclose(Ps[a] @ Ps[b], 0, atol=1e-12)  # orthogonal
    # representation property of T on the orbit
    mt = mult_table()
    for i in range(0, 48, 5):
        for j in range(0, 48, 7):
            assert np.allclose(T[i] @ T[j], T[mt[i, j]])


@pytest.mark.parametrize("shape", list(SHAPES))
def test_irrep_coefficients_deterministic_and_valid(shape):
    """Multiplicity bases must not depend on LAPACK/eigh (they did, across OSPool nodes)."""
    from rhadron.operators.gluelump import irrep_coefficients
    keys, c1 = irrep_coefficients(SHAPES[shape])
    keys, c2 = irrep_coefficients(SHAPES[shape])
    for k in c1:
        assert np.array_equal(c1[k], c2[k])
        v = c1[k]  # [row, mult, n]
        G = np.einsum("rmn,rkn->rmk", v, v)
        for r in range(v.shape[0]):
            assert np.allclose(G[r], np.eye(v.shape[1]), atol=1e-12)  # orthonormal per row


def test_canonical_basis_independent_of_input_rotation():
    """Same projector given in a different numerical form -> identical basis."""
    from rhadron.operators.gluelump import canonical_basis
    rng = np.random.default_rng(0)
    Q, _ = np.linalg.qr(rng.normal(size=(6, 2)))
    P = Q @ Q.T
    b1 = canonical_basis(P)
    Q2 = Q @ np.array([[0.0, 1.0], [-1.0, 0.0]])  # rotated basis of the same subspace
    b2 = canonical_basis(Q2 @ Q2.T)
    assert np.allclose(b1, b2, atol=1e-12)
