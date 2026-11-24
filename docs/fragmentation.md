# Deliverable: how often does a gluino end up in an R-glueball? (user request, 2026-11-24)

## What lattice QCD can and cannot give
The fraction of gluinos that hadronise into an R-glueball (g̃g) rather than an R-meson (g̃qq̄) or
R-baryon (g̃qqq) is a **fragmentation** quantity — a property of non-perturbative, non-equilibrium
hadronisation in a jet, not of the stationary spectrum.  It is not a lattice observable.  In ATLAS /
Pythia 8 it is a free parameter (`RHadrons:probGluinoball`, default 0.1 — to be verified against the
Pythia 8 manual before use).

What the lattice *does* determine, and what controls the observable outcome:
1. **The spectrum and thresholds** (M4, M5): whether the R-glueball lies below or above R-meson + π
   (or R-baryon + ...) thresholds.  If it lies above, an R-glueball produced in fragmentation decays
   strongly within ~10⁻²³ s to an R-meson, so the *detected* R-glueball fraction is ~0 whatever
   `probGluinoball` is; if it is the lightest state it is stable against strong decay.
2. **Mixing** (M5, dynamical): with sea quarks the R-glueball and the flavour-singlet (I = 0) R-mesons
   carry the same quantum numbers and mix (joint GEVP of g̃g and g̃(uū+dd̄+ss̄) operators, PLAN §1.3).
   The eigenstates' glue/quark content (operator overlaps) tells how "glueball-like" the physical
   neutral states are — the closest lattice analogue of "fraction of the time it is an R-glueball".
3. **Charged / neutral / R-glueball composition** after strong and electromagnetic decays, using the
   lattice spectrum (PLAN §1.5 deliverable).

## Planned estimate (after M5)
- Feed the lattice R-hadron offsets (ATLAS PDG-ID table, §1.5) into Pythia 8 R-hadron fragmentation
  and scan `probGluinoball`; propagate strong decays using lattice thresholds → detected fractions of
  R-glueball / neutral / charged R-mesons / R-baryons, with the fragmentation parameter as an explicit
  model uncertainty.
- Statistical-hadronisation cross-check: relative primary yields ∝ g_i exp(−ΔΛ̄_i / T_H) with
  T_H ≈ 155–160 MeV, using lattice splittings (model estimate, stated as such).
- Lattice content: R-glueball admixture of the lightest neutral state from the mixing analysis.
