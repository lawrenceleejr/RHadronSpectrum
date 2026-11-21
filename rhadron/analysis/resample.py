"""Binning, jackknife and bootstrap over configurations (axis 0)."""
import numpy as np


def bin_data(x, b):
    n = (len(x) // b) * b
    x = np.asarray(x[:n])
    return x.reshape(n // b, b, *x.shape[1:]).mean(axis=1)


def jackknife_samples(x):
    x = np.asarray(x)
    n = len(x)
    s = x.sum(axis=0)
    return (s[None] - x) / (n - 1)


def jackknife_error(samples):
    n = len(samples)
    m = samples.mean(axis=0)
    return np.sqrt((n - 1) / n * ((samples - m) ** 2).sum(axis=0))


def bootstrap_indices(n, nboot, seed=0):
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, size=(nboot, n))


def bootstrap_samples(x, idx):
    x = np.asarray(x)
    return x[idx].mean(axis=1)


def tau_int(series, S=1.5):
    """Integrated autocorrelation time with the Wolff automatic window (Gamma method)."""
    x = np.asarray(series, dtype=float)
    n = len(x)
    d = x - x.mean()
    G = np.array([np.dot(d[: n - t], d[t:]) / (n - t) for t in range(n // 2)])
    if G[0] == 0:
        return 0.5, 0.0
    rho = G / G[0]
    tau = 0.5
    for W in range(1, n // 2):
        tau = 0.5 + rho[1:W + 1].sum()
        tau_c = max(tau, 1e-6)
        g = np.exp(-W / (S * tau_c)) - S * tau_c / np.sqrt(W * n) if tau > 0.5 else -1
        if g < 0:
            break
    err = tau * np.sqrt(2 * (2 * W + 1) / n)
    return tau, err
