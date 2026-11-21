# R-Hadron Spectrum from Lattice QCD — Execution Plan

## Context

The repo `RHadronSpectrum` is empty (README only). Goal: compute the spectrum of
R-hadrons (bound states of a heavy gluino with gluons/quarks) for m_gluino ≈ 1 TeV with
modern lattice QCD, and identify the lightest state. This plan is the hand-off document:
an executor agent runs it on an HTCondor GPU cluster, milestone by milestone.
Executor conventions are in `CLAUDE.md` (mirrors §9).

> Executor note: numerical values and citations below are from memory. Milestone M0
> requires verifying every quoted parameter against the primary source before use.

---

## 1. Physics formulation (the decisions that define the project)

**1.1 Static-gluino limit.** A 1 TeV gluino cannot be a relativistic lattice field
(needs a⁻¹ ≫ 1 TeV). It does not need to be: m_g̃ ≫ Λ_QCD, so use HQET for a
colour-**adjoint** source. The gluino propagator becomes an adjoint temporal Wilson line

    U_adj^{ab}(x; t,0) = 2 Tr[ T^a U(x;t,0) T^b U†(x;t,0) ]      (real, SO(8))

and  M_R = m_g̃ + Λ̄_i + O(Λ²_QCD / m_g̃).  The correction is ~0.1–0.3 MeV at 1 TeV —
far below lattice errors. So the result is m_g̃-independent: **the spectrum is the set of
Λ̄_i**, valid for any gluino ≳ 100 GeV.

**1.2 Consequences to respect everywhere.**
- Gluino spin decouples. States are labelled by the *light* degrees of freedom:
  j^{PC}_light, flavour (I, S), baryon number B. Each level is a degenerate doublet
  J = j_light ± ½ (splitting ≲ 1 MeV, not computed).
- The lattice energy is E_i(a) = Λ̄_i + δm(a) with δm ∝ C_A/a linearly divergent but
  **identical in all channels**. Only **differences Λ̄_i − Λ̄_j** are physical and have
  a continuum limit. All headline results are splittings relative to the lightest state.
  (Absolute Λ̄ in a renormalon-subtracted scheme is optional, M7.)
- Symmetry group at the source: cubic O_h (bosonic light d.o.f.) or double cover O_h^D
  (R-baryons, half-integer j_light) ⊗ C (neutral channels) ⊗ flavour.

**1.3 Channels to compute.**

| Sector | Content | Operator at the source site x (adjoint index a) | Irreps |
|---|---|---|---|
| R-glueball ("gluelump") | g̃g | Tr[T^a B_i] (1⁺⁻), Tr[T^a E_i] (1⁻⁻), extended smeared-staple shapes | all 20 O_h ⊗ C |
| R-meson, I=1 | g̃ud̄ | q̄ Γ T^a q, Γ ∈ {γ5, γ_i, 1, γ5γ_i, γ4-variants, 1 covariant derivative} | A1, T1, (E, T2) ± |
| R-meson, I=½ | g̃us̄ | same | same |
| R-meson, I=0 | g̃(uū+dd̄), g̃ss̄ | same + disconnected; **mixes with gluelump** → joint GEVP | same |
| R-baryon | g̃qqq | colour-octet qqq, both (3̄-diquark⊗3)₈ and (6-diquark⊗3)₈; Pauli ⇒ flavour-spin in SU(6) **70**: (8,½), (8,3/2), (10,½), (1,½) | G1g/u, Hg/u |

Must-have R-baryon states: flavour-singlet *uds* j=½ (Farrar's candidate lightest
R-baryon), flavour-octet j=½ (g̃uud/g̃udd), octet j=3/2, decuplet j=½.

**1.4 Questions the project answers (deliverables).**
1. Ordered table of Λ̄_i − Λ̄_lightest (MeV) per channel with stat + syst errors.
2. Identity of the lightest R-hadron: gluelump 1⁺⁻ vs vector-like R-meson (1⁻⁻) vs
   pseudoscalar-like (0⁻⁺). Prior quenched work (Foster & Michael 1998) left these within
   ~100 MeV; colour-octet hyperfine sign suggests vector below pseudoscalar. This is the
   headline.
3. Lightest R-baryon and Δ_conv ≡ (Λ̄_baryon + m_π) − (Λ̄_meson + m_N): sign decides
   whether R-meson + N → R-baryon + π is exothermic (drives detector phenomenology).
4. Strong-decay thresholds per sector (lightest state + π, K) to say which levels are stable.

**Out of scope (state explicitly in the paper):** QED / isospin breaking (the few-MeV
charged-vs-neutral R-meson ordering), 1/m_g̃ corrections, squark effects.

---

## 2. Method choices

- **Static action:** HYP2-smeared temporal links inside U_adj (exponential S/N gain;
  adjoint noise is ~9/4 worse in the exponent than fundamental static quarks). Run a
  second static action (HYP1 or APE) on a subset: splittings must agree — a free check.
- **Light quarks:** Wilson-clover. Solves with QUDA adaptive multigrid.
- **Sources:** the static source does not move, so all quark lines start and end at the
  same spatial site. Use gauge-covariantly smeared (Gaussian/Wuppertal on stout-smeared
  links) point-to-all propagators, 2–3 smearing radii, many source sites per config with
  all-mode averaging (sloppy solves + exact bias correction). 12 solves per
  (site, flavour, smearing). Distillation is a deferred upgrade, only if operator bases
  need to grow.
- **Disconnected / mixing pieces (I=0):** gluelump↔q̄q mixing needs G(x,0;x,0) — already
  in the point-to-all solve. Loop–loop pieces need sources at the same x on several
  timeslices; schedule these source patterns from the start.
- **Gluelumps:** no solves; operators on every site and timeslice, APE/stout-smeared
  spatial links at 3–4 levels.
- **Spectroscopy:** matrix correlators C_ij(t) per (irrep, flavour), GEVP at (t0, t),
  correlated multi-exponential fits as cross-check. Splittings from the joint bootstrap
  (same configs) so δm and correlated noise cancel.
- **Errors:** bootstrap/jackknife with binning + Γ-method (pyerrors) for autocorrelation;
  systematics from fit-range/t0 variation (model average, AIC weights), static-action
  variation, a → 0, m_π dependence, volume.
- **Scale:** w0 / t0 gradient flow (r0 as cross-check, primary for quenched).

**Software stack (primary):** QUDA (GPU solvers, smearing, flow) driven from Python via
**PyQUDA** + CuPy for contractions; Chroma+QUDA only if HMC generation is needed;
analysis in NumPy/pyerrors/gvar+lsqfit; HDF5 for correlators; **HTCondor** (see §2.1).
**Fallback** if PyQUDA fails the M0 acceptance tests:
GPT (Grid Python Toolkit). Decide once in M0, record in `docs/logbook.md`, don't revisit.

### 2.1 HTCondor execution model (the cluster is HTCondor, not SLURM)

Design everything as **independent single-node, single-GPU jobs** — the natural HTCondor
unit, and a good fit: measurements are embarrassingly parallel over (config, source batch).
- **One job = one (ensemble, config, task)**; `queue ... from manifest.txt`,
  `request_gpus = 1`, plus `request_memory/disk/cpus` and a GPU-memory `require_gpus`
  constraint from `configs/cluster.yaml`. No multi-node MPI anywhere; lattice sizes are
  chosen to fit one GPU (32³×64 clover + multigrid fits in ≳ 24 GB; verify in M0).
- **Workflow = DAGMan.** One DAG per ensemble: `flow → gluelump`, `solve → contract`,
  then a final `analyze` node; `RETRY`, `MAXJOBS` throttles, and rescue DAGs give
  resumability. `workflows/manifest.py` generates the DAG + submit files from the
  ensemble YAML and skips outputs that already exist and pass a checksum.
- **Eviction-safe.** Assume jobs can be preempted: every task writes atomically
  (tmp + rename), is idempotent, and long tasks checkpoint per source batch
  (`when_to_transfer_output = ON_EXIT_OR_EVICT` or self-checkpoint exit code +
  `checkpoint_exit_code`). Keep jobs short (target ≤ 2–4 h) by batching sources.
- **HMC generation** (Stage A always; B/C only in fallback) is a serial Markov chain:
  run as a chain of self-checkpointing jobs, N trajectories each, linked in a linear DAG
  (or one self-resubmitting job). Run several independent streams in parallel to use
  the pool; treat streams as replicas in the error analysis.
- **Software delivery:** one Apptainer image (`env/apptainer.def`) with QUDA + PyQUDA +
  the `rhadron` package at a pinned git SHA, used via `container_image`. Avoids
  per-node build differences across heterogeneous GPUs; build QUDA for the oldest GPU
  architecture in the pool.
- **Data:** if a shared filesystem is visible from execute nodes, read configs / write
  correlators there directly; otherwise use Condor file transfer (or OSDF/`stash`) for
  configs in and HDF5 out, never propagators. Propagators live only on job-local
  scratch and are contracted in the same job (`solve`+`contract` fused when no shared FS).
- M0 must determine: shared FS or not, GPU models/memory in the pool, max job runtime,
  preemption policy, container support, per-user GPU quota. Record in `cluster.yaml`.

---

## 3. Ensemble strategy (staged; each stage is publishable on its own)

| Stage | Ensembles | Purpose |
|---|---|---|
| A. Quenched | Wilson plaquette β = 5.7 / 6.0 / 6.2, L ≈ 2–2.3 fm (e.g. 12³×24, 24³×48, 32³×64), 500–1000 cfgs each, self-generated (heatbath+OR). Valence NP-clover at β = 6.0, 6.2 (ALPHA c_SW), 3 κ values from m_s to ~m_s/3 | Full pipeline validation; reproduce gluelump literature; first R-meson/R-baryon ordering; continuum limit for gluelumps |
| B. Dynamical N_f=2+1 | **PACS-CS** Iwasaki + NP-clover (β=1.90, c_SW=1.715, 32³×64, a≈0.09 fm), public via JLDG/ILDG: m_π ≈ 700, 570, 410, 300 MeV sets, ~400 cfgs each | Unquenched answer with m_π dependence; string-breaking/mixing effects real |
| C. Systematics | One finer and/or one coarser dynamical spacing (public: OpenLat/CLS on request; or self-generated at published parameters with Chroma+QUDA); optional SU(3)-symmetric point for clean flavour multiplets | Continuum + chiral extrapolation of splittings |

Fallback for B if ILDG access stalls > 1 week: self-generate at PACS-CS parameters on
24³×48 at the m_π ≈ 700 and 570 MeV points (published κ, no tuning) and proceed.

Indicative cost (benchmark in M0 and replace with measured numbers): Stage A ≲ 500
GPU-h; Stage B ~10³–10⁴ GPU-h dominated by solves (400 cfgs × 4 masses × ~64 sites × 12
× flavours/smearings); Stage C comparable to B per ensemble.

---

## 4. Repository layout

```
PLAN.md  README.md  CLAUDE.md  pyproject.toml
docs/        physics.md (formalism, operator tables, derivations)  references.md
             logbook.md (dated decisions, job IDs, anomalies)  budget.md
env/         build_quda.sh  build_pyquda.sh  build_chroma.sh  modules.sh  apptainer.def
configs/     cluster.yaml (user-filled)  ensembles/*.yaml  runs/*.yaml
rhadron/
  gauge/     io.py  smear.py (APE, stout, HYP)  adjoint.py  flow.py
  static.py           adjoint static line, static actions
  groups/    oh.py  oh_double.py  (irreps, projectors, CG tables)
  operators/ gluelump.py  rmeson.py  rbaryon.py  staticlight.py (validation)
  solve/     quda.py (multigrid setup, AMA)  sources.py
  contract/  reference.py (slow NumPy, tiny lattices)  gpu.py (CuPy)
  analysis/  resample.py  gevp.py  fits.py  scale.py  extrap.py  thresholds.py
  plots/     tufte.py (style)  spectrum.py  effmass.py
  cli.py     `rhadron gen|flow|gluelump|solve|contract|analyze|plot`
workflows/   condor/*.sub (templates)  dags/ (generated)  manifest.py (DAG + submit
             generation; every task idempotent + resumable)  wrapper.sh (job entrypoint)
tests/       unit (CPU, 4³×8)  gpu/  physics/ (reference-value regression)
results/     correlators → cluster scratch (not git); fit summaries + figures in git
paper/       notes → draft
```

---

## 5. Milestones and gates (do not start M(n+1) until the gate of M(n) passes)

**M0 — Setup & verification of inputs.** Fill/read `configs/cluster.yaml`; build stack;
benchmark multigrid solve time; literature pass to verify every parameter in §3 and
reference values in §6 (Foster–Michael hep-lat/9811010; Marsh–Lewis 1309.1627;
Herr–Schlosser–Wagner 2306.09902; Bali–Pineda hep-ph/0310130; PACS-CS 0807.1661;
Della Morte–Shindler–Sommer HYP static actions; Farrar / Buccella–Farrar–Pugliese;
Kraan hep-ex/0404001). Write `docs/budget.md`.
*Gate:* stack passes plaquette + pion-correlator smoke test on GPU; budget approved by user.

**M1 — Core library + CPU reference.** gauge I/O, smearing, adjoint lines, O_h / O_h^D
projectors, slow reference contractions for all three sectors on 4³×8.
*Gate:* all §6 unit tests green in CI (no GPU).

**M2 — Quenched gluelumps.** Generate Stage A; full 20-channel spectrum at 3 spacings;
continuum limit of splittings.
*Gate:* 1⁻⁻ − 1⁺⁻ splitting and level ordering agree with literature within errors.

**M3 — Quark machinery validation.** π, ρ, N masses on quenched β=6.0 vs literature;
fundamental static-light spectrum (S, P₋, P₊ splittings) vs literature.
*Gate:* agreement within 2σ. This validates static+light contractions where precise
references exist, before trusting the new adjoint channels.

**M4 — Quenched R-mesons and R-baryons.** All §1.3 channels, 3 quark masses, 2 spacings.
*Gate:* GPU vs reference contraction agree to 1e-10 on a small lattice; symmetry tests
pass on production data; first ordering statement with errors. **User review.**

**M5 — Dynamical production (Stage B).** Including I=0 gluelump–meson mixing and
threshold analysis. *Gate:* plateau/GEVP stability documented per channel.

**M6 — Systematics (Stage C) and final numbers.** Continuum/chiral extrapolation of
splittings, full error budget, Δ_conv, stability table.

**M7 — Write-up.** Spectrum figure, tables, `paper/` draft; optional absolute Λ̄ in RS
scheme → M ≈ m_g̃^{RS} + Λ̄^{RS}.

---

## 6. Verification (built in, not bolted on)

Unit / exactness (CPU, CI):
- U_adj ∈ SO(8): orthogonal, det 1, Tr U_adj = |Tr U|² − 1.
- Every correlator invariant under a random gauge transformation to 1e-12.
- Irrep projectors idempotent, orthogonal, correct dimensions; operators built from
  rotated shapes transform correctly.
- GPU contraction == slow reference contraction (1e-10) for every operator pair.
- R-baryon operators: verify colour-octet property and flavour-spin symmetry numerically;
  forbidden combinations (e.g. flavour-decuplet j=3/2) give identically zero correlators.

Physics regression (GPU, small ensembles):
- Plaquette, r0/a, w0/a vs published values per β.
- Cross-irrep and cross-flavour correlators consistent with zero.
- C_ij(t) Hermitian, positive-definite at small t; AMA bias correction consistent with zero.
- Splittings independent of static action (HYP2 vs HYP1/APE) within errors.
- Casimir scaling of adjoint vs fundamental static potential at short distance.
- Literature gates in M2 and M3.

End-to-end: `rhadron analyze --ensemble <tag>` regenerates every table and figure from
stored correlators; a tiny 8³×16 "toy ensemble" runs the entire chain as a real DAGMan
DAG on the pool in < 30 min (also exercises eviction-resume by killing one job).

---

## 7. Known risks and what to do

| Risk | Mitigation |
|---|---|
| Adjoint-line noise kills plateaus | HYP2; larger operator bases at small t; more sites/config; coarser a; last resort anisotropic lattice or multilevel (quenched) |
| I=0 mixing / multi-hadron thresholds obscure levels | Joint gluelump+q̄q GEVP; track thresholds; quote "lightest level per sector" not resonance parameters; heavy-m_π ensembles first |
| Lightest-state ordering within errors | Compute the *difference* directly from correlated ratio of correlators; put statistics there first |
| Stack fragility (PyQUDA) | M0 acceptance tests, GPT fallback, decision frozen |
| HTCondor eviction / heterogeneous GPUs / no shared FS | §2.1: short idempotent jobs, checkpointing, one container image, fused solve+contract |
| Lattice too large for one GPU | Stay ≤ 32³×64; if Stage C needs more, use a smaller-volume or coarser ensemble rather than multi-node |
| Ensemble access delay | Stage B fallback in §3 |
| Remembered parameters wrong | M0 verification is mandatory |

---

## 8. Inputs needed from the user before/at hand-off

1. `configs/cluster.yaml` for the HTCondor pool: submit host, GPU models/count/memory,
   max job runtime and preemption policy, shared filesystem (or file-transfer only),
   Apptainer/Docker support, storage path + quota, accounting group, GPU-hour budget.
2. ILDG/JLDG registration (needed for PACS-CS configs) — or say "self-generate".
3. Confirm scope: Stage A+B is the default target; Stage C needs explicit go-ahead after M5.

---

## 9. Executor conventions (goes into `CLAUDE.md`)

- Work milestone by milestone; never skip a gate; stop and report at "User review" gates.
- Commit and push **before** running tests or submitting jobs; record job IDs, git SHA,
  and config hashes in `docs/logbook.md` and in every HDF5 output's attributes.
- Never tune a fit to reach a literature value; report disagreement as a finding.
- Blind the R-meson-vs-gluelump ordering: fix fit ranges/operator bases on splittings to
  an offset-blinded dataset, then unblind once (M4 and M5).
- All figures follow Tufte: high data-ink, no gridlines/boxes/legends where direct
  labels work, range-frame axes, small multiples for channels × ensembles, errors shown
  as the data. The spectrum figure is a level diagram: one column per (sector, irrep),
  y = Λ̄ − Λ̄_lightest in MeV, thresholds as thin grey ticks.
- Large data stays on scratch; git holds code, configs, fit summaries (JSON/CSV), figures.
- No model identifiers in commits or files.
