"""M4 review tables from the unblinded analysis JSONs (frozen choices, logbook 2026-11-23):
per J^P the operator of the equivalent pair with the smaller total error; HYP2 headline; r0 = 0.5 fm."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R0A = {"qA60": 5.369, "qA62": 7.380}
BETA = {"qA60": 6.0, "qA62": 6.2}
HBARC_R0 = 197.327 / 0.5  # MeV per (1/r0)
PAIRS = {"0- (R-pi-like)": ("g5", "g4g5"), "1- (R-rho-like)": ("gi", "g4gi"),
         "0+": ("1", "g4"), "1+": ("g5gi", "g4g5gi")}
BARYONS = {"(8,1/2) R-nucleon-like": ["octet_A_uud_A_Cg5_1o2", "octet_S_uud_A_Cgi_1o2"],
           "(8,3/2)": ["octet_S_uud_A_Cgi_3o2", "octet_A_uud_S_Cgi_3o2"],
           "(10,1/2)": ["octet_A_uuu_Cgi_1o2"],
           "(1,1/2) S0 (uds singlet)": ["octet_A_uds_singlet_Cg5_1o2", "octet_S_uds_singlet_Cgi_1o2"],
           "(8,1/2) Lambda-like (uds)": ["octet_A_uds_Lambda8_Cg5_1o2"]}
KAPPA = {"qA60": {"l1": "0.13344 (m_pi~840)", "l2": "0.13417 (m_pi~650)", "l3": "0.13455 (m_pi~525)"},
         "qA62": {"l1": "0.13460 (m_pi~815)", "l2": "0.13510 (m_pi~625)", "l3": "0.13530 (m_pi~535)"}}


def best(ch, keys):
    cand = [(np.hypot(ch[k]["dE_stat"], ch[k]["dE_syst"]), k) for k in keys if ch.get(k, {}).get("ok")
            and "a_dE_vs_gluelump_blinded" in ch[k]]
    if not cand:
        return None
    e, k = min(cand)
    return k, ch[k]["a_dE_vs_gluelump_blinded"], e


def table(tag):
    r = json.load(open(os.path.join(HERE, f"{tag}_M4_unblinded.json")))
    assert not r["blinded"], "not unblinded"
    ch, r0a = r["channels"], R0A[tag]
    rows = []
    for lr in ("l1", "l2", "l3"):
        for fl in ("ud", "us", "ss"):
            for jp, pair in PAIRS.items():
                b = best(ch, [f"HYP2/rmeson/{lr}/{fl}/{g}" for g in pair])
                if b:
                    rows.append((lr, f"R-meson {fl}", jp, b[0].split("/")[-1], b[1] * r0a, b[2] * r0a))
        for lab, ops in BARYONS.items():
            b = best(ch, [f"HYP2/rbaryon/{lr}/{o}" for o in ops])
            if b:
                rows.append((lr, "R-baryon", lab, b[0].split("/")[-1], b[1] * r0a, b[2] * r0a))
    return r, rows


def main():
    out = ["# M4 review: quenched R-hadron spectrum relative to the lightest R-glueball (1+-)", "",
           "Static gluino (adjoint Wilson line, HYP2), quenched Wilson-plaquette ensembles, NP-clover valence quarks.",
           "Entries: r0 (Lambda_bar(state) - Lambda_bar(R-glueball 1+-)), correlated jackknife on matched",
           "configurations, error = stat (+) fit-window systematic; MeV with r0 = 0.5 fm (~9 % scale ambiguity).",
           "Negative = lighter than the R-glueball.  Caveats: quenched; heavy pions (525-840 MeV);",
           "two lattice spacings, not continuum-extrapolated; local quark operators only.", ""]
    for tag in ("qA60", "qA62"):
        if not os.path.exists(os.path.join(HERE, f"{tag}_M4_unblinded.json")):
            continue
        r, rows = table(tag)
        out += [f"## beta = {BETA[tag]} ({r['ncfg']} configurations, r0/a = {R0A[tag]})", "",
                "| kappa_l | state | light j^P / multiplet | operator | r0 dE | dE [MeV] |", "|---|---|---|---|---|---|"]
        for lr, st, jp, op, d, e in rows:
            out.append(f"| {KAPPA[tag][lr]} | {st} | {jp} | {op} | {d:+.2f} ± {e:.2f} | {d * HBARC_R0:+.0f} ± {e * HBARC_R0:.0f} |")
        out.append("")
    open(os.path.join(HERE, "M4_review.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
