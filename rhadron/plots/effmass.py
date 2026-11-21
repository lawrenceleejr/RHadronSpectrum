"""Effective-mass small multiples (one panel per channel) with the AIC-averaged fit as a band."""
import numpy as np

from . import tufte
from .tufte import plt


def small_multiples(channels, path, ncol=5, ylim=None, title=None):
    """channels: list of dicts {label, t, meff, dmeff, E, dE, window}."""
    tufte.setup()
    n = len(channels)
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(1.6 * ncol, 1.3 * nrow), sharex=True, sharey=True)
    axes = np.atleast_1d(axes).ravel()
    for ax, c in zip(axes, channels):
        ok = np.isfinite(c["meff"]) & np.isfinite(c["dmeff"]) & (c["dmeff"] < 0.5)
        t, m, dm = c["t"][ok], c["meff"][ok], c["dmeff"][ok]
        if c.get("E") is not None:
            tufte.band(ax, c["window"][0], c["window"][1], c["E"], c["dE"], color=tufte.ACCENT, alpha=0.3)
        tufte.errpoints(ax, t, m, dm, ms=2)
        ax.text(0.97, 0.95, c["label"], transform=ax.transAxes, ha="right", va="top", fontsize=8)
        if ylim:
            ax.set_ylim(*ylim)
        tufte.range_frame(ax, t if len(t) else [0, 1], ylim if ylim else (m if len(m) else [0, 1]))
    for ax in axes[n:]:
        ax.axis("off")
    for ax in axes[(nrow - 1) * ncol:]:
        ax.set_xlabel("t / a")
    for r in range(nrow):
        axes[r * ncol].set_ylabel("a E_eff")
    if title:
        fig.suptitle(title, fontsize=9, x=0.02, ha="left")
    fig.savefig(path)
    plt.close(fig)
