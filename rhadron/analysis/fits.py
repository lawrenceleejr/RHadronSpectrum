"""Correlated fits of (projected) correlators: single / double exponential, with jackknife errors,
fit-range scan and AIC model averaging (Jay & Neil 2021 style weights exp(-(chi2 + 2k - 2 Ndata)/2))."""
import numpy as np
from scipy.optimize import least_squares

from .resample import jackknife_samples


def _model(p, t, nexp):
    out = np.zeros_like(t, dtype=float)
    for k in range(nexp):
        A, E = p[2 * k], p[2 * k + 1]
        if k > 0:  # higher states parameterised by positive gaps
            E = p[1] + np.sum(np.exp(p[3:2 * k + 2:2]))
        out = out + A * np.exp(-E * t)
    return out


def fit_corr(cmean, cov, t, nexp=1, p0=None):
    """Correlated chi^2 fit.  Returns (params, chi2, dof)."""
    y = cmean[t]
    Ci = np.linalg.inv(cov[np.ix_(t, t)])
    L = np.linalg.cholesky(Ci)
    if p0 is None:
        E0 = np.log(y[0] / y[1]) / (t[1] - t[0]) if y[1] > 0 and y[0] > 0 else 0.5
        A0 = y[0] * np.exp(E0 * t[0])
        p0 = [A0, E0] + sum(([A0 * 0.5, np.log(0.5)] for _ in range(nexp - 1)), [])

    def res(p):
        return L.T @ (_model(p, t.astype(float), nexp) - y)

    r = least_squares(res, p0, method="lm", max_nfev=20000)
    chi2 = float(np.sum(r.fun ** 2))
    return r.x, chi2, len(t) - len(p0)


def jackknife_fit(samples, t, nexp=1):
    """samples: per-config (or per-bin) correlator [ncfg, T].  Fits the mean with the full covariance
    and each jackknife sample with the same covariance.  Returns (E0, dE0, chi2/dof, all E0 jk)."""
    n = len(samples)
    jk = jackknife_samples(samples)
    mean = samples.mean(axis=0)
    cov = np.cov(samples, rowvar=False) / n
    p, chi2, dof = fit_corr(mean, cov, t, nexp)
    Ej = np.array([fit_corr(j, cov, t, nexp, p0=p)[0][1] for j in jk])
    err = np.sqrt((n - 1) / n * np.sum((Ej - Ej.mean()) ** 2))
    return p[1], err, chi2 / max(dof, 1), Ej


def aic_average(results):
    """results: list of dicts with keys E, dE, chi2, k (params), n (data).  Returns (E, stat, syst)."""
    w = np.array([np.exp(-0.5 * (r["chi2"] + 2 * r["k"] - 2 * r["n"])) for r in results])
    w = w / w.sum()
    E = np.array([r["E"] for r in results])
    dE = np.array([r["dE"] for r in results])
    mean = np.sum(w * E)
    stat = np.sqrt(np.sum(w * dE ** 2))
    syst = np.sqrt(np.sum(w * (E - mean) ** 2))
    return mean, stat, syst, w
