"""Array-module selection: the same code runs on NumPy (CPU, tests) and CuPy (GPU jobs)."""
import numpy as np

try:  # pragma: no cover - depends on the node
    import cupy as cp
except Exception:  # noqa: BLE001
    cp = None


def get_xp(a):
    """Return the array module (numpy or cupy) owning array ``a``."""
    if cp is not None and isinstance(a, cp.ndarray):
        return cp
    return np


def to_numpy(a):
    if cp is not None and isinstance(a, cp.ndarray):
        return cp.asnumpy(a)
    return np.asarray(a)
