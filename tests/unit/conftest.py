import numpy as np
import pytest

from rhadron.gauge.field import random_gauge

SHAPE = (8, 4, 4, 4)  # (Lt, Lz, Ly, Lx) = 4^3 x 8


@pytest.fixture(scope="session")
def rng():
    return np.random.default_rng(12345)


@pytest.fixture(scope="session")
def U(rng):
    # rough but not Haar-random: correlators carry signal at t > 0
    return random_gauge(SHAPE, rng, eps=0.5)


@pytest.fixture(scope="session")
def g(rng):
    from rhadron.gauge.field import random_su3
    return random_su3(SHAPE, rng)
