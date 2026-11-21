"""Level diagram: one column per (sector, irrep), y = Lambda - Lambda_lightest (MeV), levels as
short horizontal bars with error boxes, thresholds as thin grey ticks, direct labels."""
import numpy as np

from . import tufte
from .tufte import plt


def level_diagram(levels, path, thresholds=(), ylabel="Λ̄ − Λ̄(1⁺⁻)  [MeV]", width=0.32, title=None):
    """levels: list of dicts {column, label, y, dy (stat+syst), color(optional)};
    thresholds: list of (column or None, y, label)."""
    tufte.setup()
    cols = []
    for l in levels:
        if l["column"] not in cols:
            cols.append(l["column"])
    fig, ax = plt.subplots(figsize=(max(3.0, 0.55 * len(cols) + 1), 3.2))
    ys = []
    for l in levels:
        x = cols.index(l["column"])
        c = l.get("color", tufte.INK)
        ax.add_patch(plt.Rectangle((x - width, l["y"] - l["dy"]), 2 * width, 2 * l["dy"], color=c, alpha=0.18, lw=0))
        ax.plot([x - width, x + width], [l["y"], l["y"]], color=c, lw=1.2)
        if l.get("label"):
            ax.annotate(l["label"], (x + width, l["y"]), xytext=(2, 0), textcoords="offset points",
                        fontsize=6.5, va="center", color=c)
        ys += [l["y"] - l["dy"], l["y"] + l["dy"]]
    for col, y, lab in thresholds:
        xs = range(len(cols)) if col is None else [cols.index(col)]
        for x in xs:
            ax.plot([x - width, x + width], [y, y], color=tufte.GREY, lw=0.5)
        if lab:
            ax.annotate(lab, (max(xs) + width, y), xytext=(2, 0), textcoords="offset points", fontsize=6,
                        color=tufte.GREY, va="center")
        ys.append(y)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=90, fontsize=7)
    ax.set_xlim(-0.6, len(cols) - 0.2)
    ax.set_ylabel(ylabel)
    tufte.range_frame(ax, [0, len(cols) - 1], ys)
    ax.tick_params(axis="x", length=0)
    if title:
        ax.set_title(title, fontsize=9, loc="left")
    fig.savefig(path)
    plt.close(fig)
