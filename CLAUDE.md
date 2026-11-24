# Executor conventions

Read `PLAN.md` first. It is the specification; this file is how to work.

- Work milestone by milestone (PLAN.md §5). Never skip a gate. Stop and report at
  "User review" gates and whenever a gate fails twice.
- Numbers and citations in PLAN.md are from memory: M0 verifies each against the primary
  source before it is used. Record corrections in `docs/logbook.md`.
- The cluster is **HTCondor**: single-node, single-GPU, short, idempotent, eviction-safe
  jobs orchestrated by DAGMan (PLAN.md §2.1). No SLURM, no multi-node MPI.
- Commit and push **before** running tests or submitting jobs. Record job IDs, git SHA
  and config hashes in `docs/logbook.md` and in every HDF5 output's attributes.
- Never tune a fit to reach a literature value; report disagreement as a finding.
- Blind the R-meson-vs-gluelump ordering: fix fit ranges and operator bases on an
  offset-blinded dataset, then unblind once (M4 and M5).
- Only energy *differences* between channels are physical (the static self-energy is
  linearly divergent and common). Never quote a bare lattice energy as a mass.
- Figures follow Tufte: high data-ink, no gridlines/boxes, direct labels instead of
  legends, range-frame axes, small multiples for channels × ensembles, errors shown as
  the data. The spectrum figure is a level diagram: one column per (sector, irrep),
  y = Λ̄ − Λ̄_lightest in MeV, thresholds as thin grey ticks.
- Large data (configs, propagators, correlators) stays on cluster storage; git holds
  code, configs, fit summaries (JSON/CSV) and figures.
- Naming: call the g̃g states **R-glueballs** in prose, figures, tables and the paper (user preference,
  standard in R-hadron phenomenology; "gluinoball" in ATLAS/Pythia).  "Gluelump" is the lattice term for
  the static-limit object; mention it once where the method is introduced.  Code identifiers keep the
  `gluelump` name.
- No model identifiers in commits or files.
