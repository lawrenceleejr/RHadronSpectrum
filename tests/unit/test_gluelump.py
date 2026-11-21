import numpy as np
import pytest

from rhadron.contract.reference import gluelump_corr_reference
from rhadron.gauge.field import gauge_transform
from rhadron.gauge.smear import ape_spatial
from rhadron.operators.gluelump import build_operators, correlators, irrep_coefficients
from rhadron.operators.paths import SHAPES
from rhadron.static import static_links

TMAX = 3


@pytest.fixture(scope="module")
def setup(U):
    V = ape_spatial(U, 0.5, 1)
    V4 = static_links(U, "HYP2")
    return V, V4


def test_production_matches_reference(setup):
    V, V4 = setup
    for shape, key in (("plaq", ("T1g", "-")), ("chair", ("T1u", "+")), ("lplaq", ("A1u", "-"))):
        keys, coeffs = irrep_coefficients(SHAPES[shape])
        ops, labels = build_operators([V], shapes=[shape])
        o = ops[key][:1, :1]  # first operator, row 0
        C = correlators({key: o}, V4, TMAX)[key][:, 0, 0]
        pc = list(zip(keys, coeffs[key][0, 0]))
        Cref = gluelump_corr_reference(V, V4, pc, -1 if key[1] == "-" else 1, TMAX)
        assert np.abs(C - Cref).max() < 1e-10 * max(1, np.abs(Cref).max()), (shape, key, C, Cref)


def test_gauge_invariance(U, g):
    out = []
    for W in (U, gauge_transform(U, g)):
        V = ape_spatial(W, 0.5, 1, n_proj=40)
        V4 = static_links(W, "HYP2", n_proj=40)
        ops, _ = build_operators([V], shapes=["plaq", "chair"])
        out.append(correlators(ops, V4, TMAX))
    for k in out[0]:
        assert np.abs(out[0][k] - out[1][k]).max() < 1e-8, k


def test_correlator_unprojected_gauge_invariance_exact(U, g):
    """Without smearing (no iterative projection) gauge invariance holds to machine precision."""
    out = []
    for W in (U, gauge_transform(U, g)):
        ops, _ = build_operators([W], shapes=["plaq"])
        out.append(correlators(ops, W[3], TMAX))
    for k in out[0]:
        assert np.abs(out[0][k] - out[1][k]).max() < 1e-12, k


def test_streamed_measure_matches_full(setup):
    V, V4 = setup
    full_ops, _ = build_operators([V], shapes=["plaq", "chair"])
    full = correlators(full_ops, V4, TMAX)
    from rhadron.operators.gluelump import measure
    res, labels = measure([V], {"HYP2": V4}, TMAX, shapes=["plaq", "chair"], dtype=np.float64)
    for k in full:
        assert np.abs(full[k] - res["HYP2"][k]).max() < 1e-12, k
