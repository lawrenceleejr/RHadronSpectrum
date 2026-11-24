"""Data figures for the status report (one panel per PDF, Tufte style).
  plaq_<tag>.pdf          plaquette Monte Carlo history per stream (from job logs) vs literature
  meff_qA57_<chan>.pdf    preliminary gluelump effective masses (GEVP principal correlator), beta = 5.7
"""
import glob
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from rhadron.analysis import gluelump as GL  # noqa: E402
from rhadron.analysis.gevp import effective_mass  # noqa: E402
from rhadron.analysis.resample import jackknife_error, jackknife_samples  # noqa: E402
from rhadron.plots.tufte_helpers import save_pdf  # noqa: E402

plt.style.use(os.path.join(HERE, "..", "..", "rhadron", "plots", "tufte.mplstyle"))
DATA = "/scratch/llee/rhadron/data"
OUT = os.path.join(HERE)
INK, GREY, ACC = "#222222", "#9a9a9a", "#b2182b"
LIT = {"qA57": (5.7, 0.54900, 0.00080), "qA60": (6.0, 0.593738, 0.000017), "qA62": (6.2, 0.613647, 0.000008)}


def range_frame(ax, x, y):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_bounds(np.nanmin(x), np.nanmax(x))
    ax.spines["left"].set_bounds(np.nanmin(y), np.nanmax(y))
    ax.spines["bottom"].set_position(("outward", 4))
    ax.spines["left"].set_position(("outward", 4))


def plaquette_history(tag):
    beta, p_lit, dp = LIT[tag]
    series = {}
    for f in glob.glob(f"{DATA}/{tag}/s*/logs/{tag}_s*_u*.out"):
        s = int(re.search(r"_s(\d+)_u", f).group(1))
        for line in open(f):
            m = re.match(r"sweep (\d+) plaq ([0-9.]+)", line)
            if m:
                series.setdefault(s, {})[int(m.group(1))] = float(m.group(2))
    if not series:
        return None
    fig, ax = plt.subplots(figsize=(4.2, 2.8))
    xs, ys = [], []
    for s, d in sorted(series.items()):
        k = np.array(sorted(d))
        v = np.array([d[i] for i in k])
        ax.plot(k, v, lw=0.6, color=INK if s % 2 == 0 else GREY, alpha=0.8)
        xs += [k.min(), k.max()]
        ys += [v.min(), v.max()]
    ax.axhline(p_lit, color=ACC, lw=0.8, ls=(0, (4, 2)))
    ax.annotate(f"literature {p_lit}", (max(xs), p_lit), xytext=(4, 0), textcoords="offset points",
                color=ACC, va="center", fontsize=7)
    w = 0.0025 if beta >= 6.0 else 0.006
    lo, hi = p_lit - w, p_lit + w
    ax.set_ylim(lo, hi)
    ax.annotate("cold starts (black) and hot starts (grey)\nenter from outside the window",
                (max(xs), lo), xytext=(0, 2), textcoords="offset points", ha="right", va="bottom",
                fontsize=6.5, color=GREY)
    ax.set_xlabel("compound sweeps (1 heatbath + 4 over-relaxation)")
    ax.set_ylabel("average plaquette")
    ax.set_title(f"$\\beta = {beta}$   {len(series)} streams", loc="left", fontsize=8)
    range_frame(ax, xs, [lo, hi])
    return save_pdf(fig, os.path.join(OUT, f"plaq_{tag}.pdf"))


CHANNELS = [("T1g-", "$1^{+-}$ ($T_{1g}$)"), ("T1u-", "$1^{--}$ ($T_{1u}$)"), ("T2u-", "$2^{--}$ ($T_{2u}$)"),
            ("T2g-", "$2^{+-}$ ($T_{2g}$)"), ("A1g+", "$0^{++}$ ($A_{1g}$)"), ("A1u-", "$0^{--}$ ($A_{1u}$)")]


def gluelump_meff(tag="qA57", binsize=4, t0=1, td=2):
    files = sorted(glob.glob(f"{DATA}/{tag}/s*/out/{tag}_s*_c*_glue.h5"))
    data, meta = GL.load(files, "HYP2")
    out = []
    for key, label in CHANNELS:
        if key not in data:
            continue
        pc, nb = GL.principal_correlator(data[key], t0, td)
        pcb = GL.binned(pc, meta, binsize)
        jk = jackknife_samples(pcb)
        me = np.array([effective_mass(j) for j in jk])
        m = effective_mass(pcb.mean(axis=0))
        dm = jackknife_error(me)
        t = np.arange(len(m)) + 0.5
        ok = np.isfinite(m) & np.isfinite(dm) & (dm < 0.6) & (t > 0.6)
        if ok.sum() < 2:
            continue
        fig, ax = plt.subplots(figsize=(3.0, 2.4))
        ax.errorbar(t[ok], m[ok], yerr=dm[ok], fmt="o", ms=3, color=INK, elinewidth=0.8, capsize=0, mew=0)
        ax.set_xlabel("$t/a$")
        ax.set_ylabel("$a E_{\\rm eff}$")
        ax.set_title(f"{label}   $\\beta = 5.7$, {len(meta)} cfgs, {nb} ops", loc="left", fontsize=7.5)
        ax.text(0.98, 0.04, "preliminary, unfitted", transform=ax.transAxes, ha="right", fontsize=6.5, color=GREY)
        range_frame(ax, t[ok], np.concatenate([m[ok] - dm[ok], m[ok] + dm[ok]]))
        out.append(save_pdf(fig, os.path.join(OUT, f"meff_{tag}_{key.replace('-', 'm').replace('+', 'p')}.pdf")))
        plt.close(fig)
    return out


if __name__ == "__main__":
    for tag in ("qA57", "qA60", "qA62"):
        print(plaquette_history(tag))
    for p in gluelump_meff():
        print(p)


def good_files(tag, fix="c7187ab"):
    import subprocess

    import h5py
    out = []
    for f in sorted(glob.glob(f"{DATA}/{tag}/s*/out/{tag}_s*_c*_glue.h5")):
        sha = str(h5py.File(f, "r").attrs.get("git_sha", ""))
        if subprocess.run(["git", "merge-base", "--is-ancestor", fix, sha], capture_output=True).returncode == 0:
            out.append(f)
    return out


def level_diagram_from_json(path, tag, r0a, beta, a_fm=None, max_err=0.5):
    import json
    res = json.load(open(path))
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    order = ["T1g-", "T1u-", "T2u-", "Eu-", "T2g-", "Eg-", "A2g-", "A1g+", "Eg+", "T2u+"]
    names = {"T1g-": "$1^{+-}$", "T1u-": "$1^{--}$", "T2u-": "$2^{--}$", "Eu-": "$2^{--}$",
             "T2g-": "$2^{+-}$", "Eg-": "$2^{+-}$", "A2g-": "$3^{+-}$", "A1g+": "$0^{++}$",
             "Eg+": "$2^{++}$", "T2u+": "$2^{-+}$"}
    xs, ys = [], []
    def usable(k):
        c = res["channels"].get(k, {})
        return c.get("ok") and r0a * float(np.hypot(c.get("a_dE_stat", 9), c.get("a_dE_syst", 9))) <= max_err

    dropped = [k for k in order if res["channels"].get(k, {}).get("ok") and not usable(k)]
    for i, k in enumerate([k for k in order if usable(k)]):
        c = res["channels"][k]
        y = r0a * c["a_dE"]
        dy = r0a * float(np.hypot(c["a_dE_stat"], c["a_dE_syst"]))
        ax.add_patch(plt.Rectangle((i - 0.32, y - dy), 0.64, 2 * dy, color=INK, alpha=0.15, lw=0))
        ax.plot([i - 0.32, i + 0.32], [y, y], color=INK, lw=1.2)
        ax.annotate(names[k], (i, y + dy), xytext=(0, 2), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7)
        xs.append(i)
        ys += [y - dy, y + dy]
    hsw, dhsw = 0.87, 0.09  # Herr-Schlosser-Wagner continuum 1-- - 1+- (r0 = 0.5 fm), docs/references.md
    ax.plot([0.68, 1.32], [hsw, hsw], color=ACC, lw=0.8, ls=(0, (3, 2)))
    ax.annotate("continuum lit.", (1.32, hsw), xytext=(3, 0), textcoords="offset points", fontsize=6, color=ACC,
                va="center")
    ks = [k for k in order if usable(k)]
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels([f"{k[:-1]}{k[-1]}" for k in ks], fontsize=6, rotation=0)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("$r_0\\,(\\bar\\Lambda - \\bar\\Lambda_{1^{+-}})$")
    sp = f" ($a \\approx {a_fm}$ fm)" if a_fm else ""
    ax.set_title(f"R-glueball levels (static gluino), $\\beta = {beta}${sp}, {res['ncfg']} cfgs, HYP2", loc="left", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_bounds(min(ys), max(ys))
    ax.spines["left"].set_position(("outward", 4))
    note = "single lattice spacing: not continuum extrapolated"
    if dropped:
        note += f"; not shown (error above {max_err}/r0): " + ", ".join(dropped)
    ax.text(0.0, -0.14, note, transform=ax.transAxes, fontsize=6, color=GREY)
    return save_pdf(fig, os.path.join(OUT, f"levels_{tag}.pdf"))


def gluelump_overlay(tag="qA57", binsize=4, t0=1, td=2):
    """All main channels on one panel, direct labels at the last reliable point."""
    files = good_files(tag)
    data, meta = GL.load(files, "HYP2")
    cols = {"T1g-": INK, "T1u-": ACC, "T2u-": "#2166ac", "T2g-": "#4d9221", "A1g+": "#8c510a"}
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    allx, ally = [], []
    for i, (key, label) in enumerate(CHANNELS):
        if key not in cols or key not in data:
            continue
        pc, nb = GL.principal_correlator(data[key], t0, td)
        pcb = GL.binned(pc, meta, binsize)
        me = np.array([effective_mass(j) for j in jackknife_samples(pcb)])
        m, dm = effective_mass(pcb.mean(axis=0)), jackknife_error(me)
        t = np.arange(len(m)) + 0.5 + 0.06 * (i - 2)
        ok = np.isfinite(m) & np.isfinite(dm) & (dm < 0.12)
        if ok.sum() < 2:
            continue
        ax.errorbar(t[ok], m[ok], yerr=dm[ok], fmt="o-", ms=2.5, lw=0.5, color=cols[key], elinewidth=0.8,
                    capsize=0, mew=0)
        j = np.nonzero(ok)[0][-1]
        ax.annotate(label, (t[j], m[j]), xytext=(5, 0), textcoords="offset points", va="center",
                    fontsize=7, color=cols[key])
        allx += list(t[ok])
        ally += list(m[ok] - dm[ok]) + list(m[ok] + dm[ok])
    ax.set_xlabel("$t/a$")
    ax.set_ylabel("$a E_{\\rm eff}$  (includes the common static self-energy)")
    ax.set_title(f"R-glueball effective masses, $\\beta = 5.7$, {len(meta)} configurations", loc="left", fontsize=8)
    ax.text(0.0, -0.22, "preliminary: GEVP principal correlators, no fits; only differences between channels are physical",
            transform=ax.transAxes, fontsize=6, color=GREY)
    range_frame(ax, allx, ally)
    return save_pdf(fig, os.path.join(OUT, f"meff_{tag}_overlay.pdf"))


if __name__ == "__main__":
    print(gluelump_overlay())
    print(level_diagram_from_json(os.path.join(HERE, "..", "qA57_gluelump_HYP2.json"), "qA57", 2.922, 5.7))
