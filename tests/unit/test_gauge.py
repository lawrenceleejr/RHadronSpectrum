import numpy as np
import pytest

from rhadron.gauge.field import (dag, gauge_transform, plaquette, project_su3, random_su3, trace,
                                 unit_gauge)
from rhadron.gauge.smear import HYP_PARAMS, ape_spatial, hyp_links, stout_spatial
from rhadron.static import TA, static_links, to_adjoint


def test_unit_plaquette():
    assert np.allclose(plaquette(unit_gauge((4, 4, 4, 4))), 1.0)


def test_links_su3(U):
    assert np.abs(U @ dag(U) - np.eye(3)).max() < 1e-12
    assert np.abs(np.linalg.det(U) - 1).max() < 1e-12


def test_plaquette_gauge_invariant(U, g):
    assert np.allclose(plaquette(U), plaquette(gauge_transform(U, g)), atol=1e-12)


def test_projection_is_su3_and_idempotent(rng):
    V = random_su3((20,), rng)
    M = V + 0.4 * (rng.normal(size=(20, 3, 3)) + 1j * rng.normal(size=(20, 3, 3)))
    P = project_su3(M, 30)
    assert np.abs(P @ dag(P) - np.eye(3)).max() < 1e-12
    assert np.abs(np.linalg.det(P) - 1).max() < 1e-12
    assert np.abs(project_su3(V) - V).max() < 1e-12


def test_projection_gauge_covariant(rng):
    V = random_su3((20,), rng)
    M = V + 0.4 * (rng.normal(size=(20, 3, 3)) + 1j * rng.normal(size=(20, 3, 3)))
    a, b = random_su3((20,), rng), random_su3((20,), rng)
    assert np.abs(project_su3(a @ M @ dag(b), 40) - a @ project_su3(M, 40) @ dag(b)).max() < 1e-8


@pytest.mark.parametrize("smear", ["ape", "stout", "hyp2"])
def test_smearing_gauge_covariant(U, g, smear):
    Ug = gauge_transform(U, g)
    if smear == "ape":
        a, b = ape_spatial(U, 0.5, 2, n_proj=40), ape_spatial(Ug, 0.5, 2, n_proj=40)
        a = gauge_transform(a, g)
        assert np.abs(a[:3] - b[:3]).max() < 1e-8
    elif smear == "stout":
        a, b = gauge_transform(stout_spatial(U, 0.1, 2), g), stout_spatial(Ug, 0.1, 2)
        assert np.abs(a - b).max() < 1e-10
    else:
        from rhadron.gauge.field import mul, shift
        v = hyp_links(U, HYP_PARAMS["HYP2"], n_proj=40)[3]
        vg = hyp_links(Ug, HYP_PARAMS["HYP2"], n_proj=40)[3]
        assert np.abs(mul(mul(g, v), dag(shift(g, 3, 1))) - vg).max() < 1e-8


def test_smeared_links_su3(U):
    for V4 in (static_links(U, "HYP2"), static_links(U, "HYP1"), static_links(U, "APE")):
        assert np.abs(V4 @ dag(V4) - np.eye(3)).max() < 1e-12
        assert np.abs(np.linalg.det(V4) - 1).max() < 1e-12


def test_adjoint_so8(U):
    W = U[3, 0]
    R = to_adjoint(W)
    assert np.isrealobj(R)
    assert np.abs(R @ R.swapaxes(-1, -2) - np.eye(8)).max() < 1e-12
    assert np.abs(np.linalg.det(R) - 1).max() < 1e-12
    assert np.abs(np.trace(R, axis1=-2, axis2=-1) - (np.abs(trace(W)) ** 2 - 1)).max() < 1e-12
    # homomorphism R(AB) = R(A) R(B)
    A, B = U[0, 0], U[1, 0]
    assert np.abs(to_adjoint(A @ B) - to_adjoint(A) @ to_adjoint(B)).max() < 1e-12


def test_generators():
    assert np.allclose(np.einsum("aij,bji->ab", TA, TA), 0.5 * np.eye(8))
