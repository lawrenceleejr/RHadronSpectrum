# Path to a physical prediction with reduced errors (user request 2026-11-27)

User: "Do whatever you need to do to get to a solid physics prediction for the physical mass
splittings and ordering … get the error bars reduced."  Interpreted as approval of Stage C (lighter
dynamical pions, second dynamical spacing) within the 20,000 GPU-h ceiling.

## Error budget at M4 (β = 6.0, 293 cfgs)
Splittings to the R-glueball: total ≈ 0.13–0.18 r0, dominated by the fit-window systematic (≈ 2×
statistical), mainly from the R-glueball reference (aE error 0.0215).  → better operators (earlier
plateaus) matter more than raw statistics.

## Actions
A. Quenched β = 6.0: quark data on all 600 cfgs (16 sources for the new 300). [DAG qA60_quark_all]
B. Enlarged R-glueball basis on all quenched cfgs: 4 smearing levels, + rectangle loop, t_max + 2.
   [DAGs q*_glue_v2]  Old (2-level) files kept in ~/rhadron_persist/correlators/*/gluelump_v1;
   analyses never mix bases (modal-shape filter).
C. Cross-correlators between equivalent quark operators → 4×4 GEVP (R-mesons per j^P and flavour,
   R-baryon groups (8,½), (8,3/2), (1,½)); re-contraction of stored propagators. [qA60_recontract_x]
D. Stage C dynamical ensembles: dB410 (κ_ud 0.13754, 24³×48), dB300 (κ_ud 0.13770, 32³×64);
   HMC benchmarks first (cluster 43307054).
E. Second dynamical lattice spacing (continuum limit): parameters from docs/stageC_parameters.md
   (literature lookup in progress).
F. Final analysis: splittings ΔΛ̄ in r0 (or w0) units, combined fit
   ΔΛ̄(m_π, a) = ΔΛ̄_phys + c1 (m_π² − m_π,phys²) + c2 a² (+ alternative forms for the model
   average), AIC model averaging over fit forms; errors: stat ⊕ fit-window ⊕ chiral-form ⊕ a² form ⊕
   static action (HYP1 vs HYP2) ⊕ scale ⊕ finite volume (m_πL ≥ 4).  Quenched results serve as a
   cross-check (they do not enter the physical prediction).
G. Statistical improvements if still needed: all-mode averaging (cheap sloppy solves on many more
   source sites + exact bias correction), more sources per configuration.

## Budget (estimate, GPU-h)
Spent so far ≈ 1,500.  A ≈ 150, B ≈ 200, C ≈ 50; Stage B (dB700, dB570) ≈ 250 HMC + 600 measurements;
Stage C dB410 ≈ 400 + 300, dB300 ≈ 1,500 + 800 (to be measured); second spacing ≈ 4,000–6,000.
Total ≈ 10,000–12,000 GPU-h < 20,000.
