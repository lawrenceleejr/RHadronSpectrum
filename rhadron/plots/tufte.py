"""Tufte style for all project figures: high data-ink, no gridlines/boxes/legends, range frames,
direct labels, errors drawn as the data."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

INK = "#222222"
GREY = "#999999"
ACCENT = "#b2182b"


def setup():
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.linewidth": 0.6, "axes.edgecolor": INK,
        "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "xtick.major.width": 0.6,
        "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "axes.grid": False,
        "legend.frameon": False, "savefig.bbox": "tight", "pdf.fonttype": 42,
    })


def range_frame(ax, x, y, pad=0.0):
    """Spines span only the data range; top/right removed."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    x, y = np.asarray(x, float), np.asarray(y, float)
    x, y = x[np.isfinite(x)], y[np.isfinite(y)]
    if len(x):
        ax.spines["bottom"].set_bounds(x.min(), x.max())
    if len(y):
        ax.spines["left"].set_bounds(y.min(), y.max())
    ax.spines["bottom"].set_position(("outward", 4))
    ax.spines["left"].set_position(("outward", 4))


def errpoints(ax, x, y, dy, color=INK, label=None, label_side="right", ms=3):
    ax.errorbar(x, y, yerr=dy, fmt="o", ms=ms, color=color, elinewidth=0.8, capsize=0, mew=0)
    if label is not None and len(x):
        i = -1 if label_side == "right" else 0
        ax.annotate(label, (x[i], y[i]), xytext=(6 if label_side == "right" else -6, 0),
                    textcoords="offset points", va="center", ha="left" if label_side == "right" else "right",
                    color=color, fontsize=8)


def band(ax, x0, x1, y, dy, color=GREY, alpha=0.25):
    ax.fill_between([x0, x1], [y - dy] * 2, [y + dy] * 2, color=color, alpha=alpha, lw=0)
    ax.plot([x0, x1], [y, y], color=color, lw=0.8)
