# Logbook

Dated decisions, job IDs, anomalies.  Times are UTC dates.

## 2026-11-20 — M0 start (ap23.uc.osg-htc.org)

- Repo cloned to `~/RHadronSpectrum`, branch `claude/osg-execution`; push via SSH remote works.
- Merged plan addendum (§1.5 ATLAS benchmark ATL-PHYS-PUB-2019-019) from `claude/pensive-cannon-mlgwym`.
- User decisions (PLAN §8): no ILDG/JLDG registration -> Stage B by self-generation fallback
  (PACS-CS parameters, 24³×48, two heaviest pion masses) unless configs are freely downloadable;
  budget gate delegated with a ceiling of ~20,000 GPU-h; scope Stages A+B; M4 review is
  report-and-continue.
- Cluster facts (configs/cluster.yaml): OSPool, no shared FS on execute nodes, OSDF project area
  `/ospool/uc-shared/project/futurecolliders/llee/rhadron`; MAX_TRANSFER_INPUT_MB = 5000;
  ~185 GPU slots of 13 models, driver CUDA >= 12.4 everywhere; ~100 slots with >= 15 GB and cc >= 7.0.
- Decision: the gluelump sector and quenched gauge generation need no Dirac solves; they run as
  **CPU jobs** with the vectorised NumPy code (same code runs on CuPy). GPUs are used for light-quark
  solves only. This makes Stage A cheap in GPU-hours.
- Decision: container from `nvidia/cuda:12.4.1-devel-ubuntu22.04`; QUDA develop @ af7e150 built as a
  fat binary (sm_70, 75, 80, 86, 89, 90 + compute_90 PTX); CMake target patched to accept the list
  (feature level stays sm_70).  lsqfit dropped (its `vegas` dependency fails to build); fits use
  scipy + gvar.
- Only local quark operators at the static site are used initially; for these O_h^D irreps are
  fixed by continuum spin (j=1/2 -> G1, j=3/2 -> H), so the double-cover projectors reduce to
  spin projectors. Extended quark operators (and the full O_h^D machinery) only if bases must grow.

## 2026-11-20 — M0 literature verification (docs/references.md)

Full tables with source pointers in `docs/references.md` (19 corrections to PLAN.md listed there).
Decisions taken from it:
- **Stage B data access:** PACS-CS/JLDG downloads require a grid certificate registered with the
  ILDG/JLDG VO (no anonymous route) -> self-generation fallback confirmed: Iwasaki + NP clover,
  β = 1.90, c_SW = 1.715, (κ_ud, κ_s) = (0.13700, 0.13640) [m_π ≈ 702 MeV] and (0.13727, 0.13640)
  [m_π ≈ 570 MeV], 24³×48 (m_π L ≈ 7.7, 6.3), a ≈ 0.0907 fm.
- **Second static action:** HYP1 (α = 0.75, 0.6, 0.3), not ALPHA "APE"/"s" (non-unitary links break
  the SO(8) property). Primary HYP2 (1.0, 1.0, 0.5).
- **M2 gate reference:** Herr–Schlosser–Wagner 2306.09902 Tab. 4 (continuum quenched gluelumps),
  compared in r0 units: 1⁻⁻ − 1⁺⁻ = 0.342(36) GeV at r0 = 0.5 fm (≈ 0.87/r0); Foster–Michael
  0.933(18)/r0 as second reference; ordering 1⁺⁻ < 1⁻⁻ < 2⁻⁻ < 2⁺⁻ < 0⁺⁺. Marsh–Lewis is N_f=2+1
  (not a quenched reference); 2501.15670 gives figures only (not a gate).
- **Quenched scales:** plaquette 0.593738(17) (β=6.0), 0.613647(8) (β=6.2), 0.54900(80) (β=5.7);
  r0/a = 2.922(9), 5.369(9), 7.380(26). NP c_SW (ALPHA) valid β ≥ 6.0: 1.769 (6.0), 1.614 (6.2).
- **M3 gate references:** UKQCD hep-lat/9910022 β=6.0 NP clover κ = 0.13344, 0.13417, 0.13455
  (a m_π = 0.3952, 0.3048, 0.2457); static-light: quenched BGR 0809.1103 (P₋, P₊ − S ≈ 435(15),
  423(13) MeV, degenerate), ETMC continuum 1004.4235 as dynamical comparison.
- **Unquenched R-hadrons:** one preliminary R-meson study (2603.29581, N_f=3+1, effective masses only);
  no R-baryon lattice computation found. Foster–Michael: M(vector) − G(1⁺⁻) = 47(90) MeV.
- **ATLAS benchmark:** PLAN §1.5 quotes the Pythia6 column; ATLAS defaults are R-ρ 0.717, R-K* 0.886,
  R-φ 1.054, R-Λ⁰ 0.715, gluinoball 0.700 GeV. The model does include colour-magnetic splittings but
  only J=1 R-mesons. Both columns will be carried in the comparison table.

## 2026-11-21 — M0/M1 progress, Stage A production started

- Gen image `rhadron-gen-v2.sif` (CuPy + CUDA headers, no QUDA) on OSDF; v1 lacked headers for CuPy
  JIT (bench cluster 43198961 failed, fixed). Benchmarks: cluster 43199466 (see docs/budget.md).
- Toy end-to-end DAG (8³×16, 2 streams × 3 segments, gluelumps fused): DAGMan 43199618, ~6 min,
  all segments resumed from checkpoints; one transient OSDF TLS hold at CHTC-Spark auto-released.
  Plaquette (β=5.7, toy) → 0.550–0.553 (literature 0.54900(80) large volume).
- Unit tests: 50+ CPU tests green except baryon NR tests still running at time of writing.
  Fixed during M1: clover term Hermiticity (σ_μν = iγ_μγ_ν), two einsum index drops in R-baryon
  tensors, SU(6) Pauli test now uses NR (upper-component) operators where the classification is exact.
- Stage A production DAGs submitted (code a21ada7):
  qA57 DAGMan 43200189 (10 streams, MAXJOBS 4), qA60 43200191 (10 streams, MAXJOBS 8),
  qA62 43200192 (16 streams, MAXJOBS 8, cc >= 7.0 and >= 15 GB).
- Eviction-resume test postponed to a production qA60 job (toy segments too short to vacate mid-run).

## 2026-11-21 — M1 gate passed

- `pytest tests/unit` on code c9f2969: **58 passed** (CPU, 4³×8; 60 min on the
  contended AP). Covers: SU(3)/projection, gauge covariance of APE/stout/HYP, U_adj ∈ SO(8) with
  Tr U_adj = |Tr U|² − 1, O_h irreps (homomorphism, character orthonormality), row projectors
  idempotent/orthogonal/complete on every shape orbit, gluelump production == reference (1e-10) and
  gauge invariant (1e-12 unsmeared), streamed measure == full, R-meson / R-baryon production ==
  explicit Wick reference (1e-10), fast flavour-decomposed R-baryon == general tensor, gauge
  invariance of R-meson / R-baryon / static-light, colour-octet property of K^a, SU(6) Pauli pattern
  for NR operators ((10,3/2), (1,3/2) vanish; (8,½), (10,½), (1,½), (8,3/2) nonzero; colour-singlet
  56 check), exact diquark Pauli zero, production R-baryon list nonvanishing, fast nucleon == general,
  pion positivity.
- Eviction test (qA60 stream 8, job 43202007, vacated 05:03 UTC at sweep 410): spooled checkpoint
  at sweep 400 found in the job spool; resume confirmation pending job completion.
  Plaquette β=6.0, 24³×48: 0.5933–0.5938 (literature 0.593738(17)).

## 2026-11-21 — M0 GPU smoke passed; FP64 GPU restriction for generation

- M0 smoke (job 43204512.0, H100): QUDA clover propagator == CPU reference to 9.9e-14 with our
  clover sign (−κ c_SW σ_μν F_μν); QUDA solution = 2κ × ours (asymmetric mass normalisation);
  QUDA plaquette == ours. 5.2 GB image via OSDF container_image works.
- Remaining M0 items (pion correlator, MG solve timing for the budget): measq benchmark 43206157.
- Stage A first segments much slower than benchmarked on many nodes (qA57 3.9 h vs ~0.75 h; qA62
  > 4.7 h vs ~1.1 h). Cause: complex128 CuPy kernels on low-FP64 GPUs (A40/3090/A5000/L40, 1/32-1/64
  rate). Future generation nodes restricted to cc 7.0/8.0/9.0 (V100/A100/H100) by editing the
  dag gen.sub files (applies at next submission); manifest default changed. Running jobs left to finish.
- qA57: first segments complete, 344 configurations measured; qA60: 56.

## 2026-11-21 — New deliverable: lattice "picture" of the lightest state (docs/visualization.md)

- User request: final Blender animation of the lightest R-hadron's spatial structure ("soupy QCD").
- Decision: paired point sources (same spatial site, t0 and t0 + pair_sep) for all quark solves
  (`pair_sep: 12` at β = 6.0), so light-quark charge/matter densities around the gluino come from
  the same solves as the spectrum.  Density contraction to be implemented in the solve job before
  M4 production; gluonic energy density and flowed-vacuum foam from stored configurations.
- Visuals made so far: TikZ sector schematic + pipeline, Blender stills, Tufte data plots
  (results/visuals, paper/figures).
- measq single-job design abandoned (benchmark jobs ran > 3 h with no output, no eviction spool);
  replaced by resumable per-role solve jobs + per-config contraction job (timing test 43207076).

## 2026-11-21 — M0 gate passed

- GPU stack: QUDA == CPU reference propagator (9.9e-14), plaquette identical (job 43204512.0, H100).
- Pion correlator smoke test (qA60_s0_c0003, one source, cluster 43207478): positive; a·m_eff at
  t = 8-10: 0.42 (κ = 0.13344) and 0.24-0.29 (κ = 0.13455) vs UKQCD 0.395 / 0.246 — consistent at
  one-configuration noise.  MG and BiCGStab propagators give identical correlators.
- Wuppertal smearing rewritten (timeslice-restricted, batched): one smeared source 380-850 s → 5-26 s.
- Solver choice β = 6.0: mixed BiCGStab (no MG); budget docs/budget.md: total A+B ≈ 3.5-4.5k GPU-h
  ≪ 20k ceiling → delegated budget gate passed.
- Eviction-resume test **passed**: qA60 stream 8 (job 43202007) vacated at sweep 410, restarted on a
  new node and logged "resume from out/qA60_s8_ckpt.h5 at sweep 400".

## 2026-11-21 — ANOMALY found and fixed: non-deterministic gluelump operator basis

- Symptom: binning study at β=5.7 showed jackknife errors of the GEVP-projected T1g⁻ correlator
  growing like √(bin size) with no plateau, while the raw plaquette-operator correlator had
  negligible autocorrelation (lag-1 ≤ 0.15) and consistent stream means.
- Diagnosis: operators with multiplicity > 1 in an irrep (chair: 2, L-loop: 3) had their basis
  inside the degenerate subspace taken from `numpy.linalg.eigh`, which is arbitrary and differed
  between execution environments: first-segment files have the two chair T1g⁻ operators swapped
  relative to later segments (C(0) = 0.14 ↔ 4.2; subspace trace preserved 4.38 vs 4.27).
  Re-measuring a first-segment configuration on the AP with the same code reproduced the
  later-segment basis.  Averaging matrices in different bases over configurations is invalid.
- Fix (c7187ab): `canonical_basis` (Gram–Schmidt on projected unit vectors in fixed order, sign
  fixed) — platform independent; tests added.  Generation DAG code refreshed.
- Data repair: all gluelump files produced before c7187ab are re-measured from the stored
  configurations (`rhadron glue`, `manifest.py glue --good-since c7187ab`): qA57 DAGMan 43207588
  (902 cfgs), qA60 43207589 (184), qA62 43207590 (3).  Files from segments still running old code
  will be caught by a second re-measurement pass.  No physics result had been derived from the
  affected data (the earlier effective-mass overlay is superseded).

## 2026-11-21 — First gluelump spectrum, β = 5.7 (corrected data)

- Re-measurement pass 1 complete (DAGMans 43207588/89/90); pass 2 for stragglers / old-code
  segments: 43214632 (qA57, 14), 43214633 (qA60, 44), 43214634 (qA62, 6).
- Binning study on the 986 fixed-basis qA57 files: jackknife error ratio vs bin size 1/2/4/8/16 =
  1.00/0.99/0.98/0.97/1.13 (T1g⁻), 1.00/1.03/1.05/1.11/1.05 (T1u⁻) → plateau; bin size 4 fixed a priori.
- Analysis (HYP2, GEVP t0 = 1, td = 2, pruned basis, correlated single-exp AIC average over windows,
  results/qA57_gluelump_HYP2.json): ordering 1⁺⁻ < 1⁻⁻ < 2⁻⁻ < (3⁺⁻ ≈ 2⁺⁻) < 0⁺⁺ < 2⁺⁺ < 2⁻⁺;
  cubic-symmetry check: T2u⁻/Eu⁻ (2⁻⁻) and T2g⁻/Eg⁻ (2⁺⁻) degenerate within errors.
  r0 (Λ̄(1⁻⁻) − Λ̄(1⁺⁻)) = 1.13(10) at β = 5.7 (r0/a = 2.922), stable vs t_min = 2, 3
  (1.133, 1.135; t_min = 4: 0.92(36)).  Continuum literature 0.87(9) (HSW), 0.933(18) (FM).
  Not a gate comparison: M2 gate is defined on the continuum limit (β = 6.0, 6.2 pending).
  Fit policy unchanged (no tuning toward literature).
- Quark test DAG: solve jobs OK (~4 min per κ on A100 after fp32 smearing); contraction failed on
  HDF5 group iteration (fixed, rescue DAG 43214627).  Resource request lowered (8 GB, 1 CPU,
  GPU ≥ 20 GB) after better-analyze showed a single matching slot.

## 2026-11-21 — Quark chain validated; M3 production started (β = 6.0)

- Test DAG (4 cfgs × 4 κ): solve ~4 min per κ (A100), contraction 3 min per config (GPU).
  4-config pion l1: a·m_eff = 0.39-0.40 at t = 7-13 (UKQCD 0.3952 / 0.3977); static-light positive.
  R-hadron channels not inspected (blinded).
- M3 production: every 4th qA60 configuration (DAGMan below), same solves feed M4.
- Density (three-point) contraction for the final visualisation will be added before Stage B
  production (where the final physics and the "lightest state" picture come from); quenched solves
  are not repeated for it.

## 2026-11-22 — β = 6.0 gluelump spectrum (interim, 454 cfgs)

- Re-measure pass 2 nearly done (qA57 1000/1000 fixed; qA60 454/480; qA62 12/18).
- qA60 binning flat (ratios 1.00-1.06 up to bin 8); bin 4.  results/qA60_gluelump_HYP2.json.
- r0 (Λ̄(1⁻⁻) − Λ̄(1⁺⁻)) = 1.06(30) at β = 6.0 (r0/a = 5.369) vs 1.13(10) at β = 5.7.  The β = 6.0
  error is dominated by the AIC window spread (adjoint-line noise grows at finer a).  Ordering of the
  low-lying levels matches the literature.  T2g⁻ and A2u⁻ fits latch onto late noisy windows
  (errors ≈ 2/r0) — flagged unreliable; more statistics (target 600) and β = 6.2 needed before the
  M2 continuum gate.  Fit policy unchanged.
- M3 DAG 43215648: 29 nodes done in 2 h, 45 evictions (GPU slot preemption); resumable solve jobs
  absorb this; projected ~1.5 days for 101 cfgs.

## 2026-11-22 — Stage B HMC benchmark

- 43216906: QUDA abort "max_element(0) appears unset" (half-precision clover in the RHMC multishift
  force) → fermion monomials forced to double/single precision.
- 43217035: forced acceptance during warm-up (n_warm_noreject = 20) accepted dH = 22, 3, 12 →
  "Clover trlog has returned nan, clover matrix non HPD" → normal Metropolis from trajectory 1,
  τ = 0.5, finer integrator.
- 43217157: 12 trajectories, 38-72 s each on V100, acceptance 67%, plaquette 0.69 → 0.58.
  Stage B HMC ≈ 250 V100-h total (docs/budget.md).  n_outer raised to 12.
- Stage B production (M5) is NOT started: gates M2-M4 still open.  Two gen segments held at the
  20 h OSPool limit (slow GPUs before the FP64 restriction) were retargeted and released.

## 2026-11-22 — Density three-point function implemented and validated

- `rhadron/contract/density.py`: I=1 R-meson, local bilinear inserted at τ = t0 + pair_sep/2 on the
  quark and antiquark lines; CPU test: fast == explicit reference (1e-10), gauge invariant (1e-7).
- Wired into `solve_role` behind `densities: true` (off for running Stage A production).  GPU test
  (43217277, H100, qA60_s0_c0003, one pair): densities 0.4 s per pair; Re Σ_y C3 for the charge
  density (J = γ4) exactly opposite on quark vs antiquark line (γ5-hermiticity, degenerate u/d);
  matter density (J = 1) same sign on both lines, as expected.  Profiles need ensemble statistics.
- Plan: enable `densities: true` for Stage B quark production (final visualisation).

## 2026-11-22 — M3 gate, attempt 1: FAILED (nucleon); attempt-2 method pre-registered

- 49 qA60 configs (every 4th), results/qA60_M3.json.  π, ρ at all three κ agree with UKQCD 32³×64
  (pulls −0.6 … +1.0).  Static-light P₋ − S: 418(84), 443(88), 438(74) MeV; chiral (linear in
  (a m_π)²) 455(127) MeV vs BGR 435(17): pull +0.16.  Heavy-spin partners (Γ = 1 vs γ5γ_x) give
  identical energies (exact for a static quark).
- Nucleon: a m_N = 0.897(20), 0.791(20), 0.722(20) vs UKQCD 0.799, 0.700, 0.641: pulls +4.4, +3.7,
  +2.9 → gate fails.  Diagnosis: effective mass drifts down 0.90–0.96 (t = 4–8) → 0.84–0.88
  (t = 9–13), i.e. excited-state contamination (smeared source, point sink); the AIC average was
  dominated by early, precise windows (χ²/dof ≈ 0.8 cannot detect the drift).  No sign of a
  contraction error (π, ρ agree; nucleon contraction unit-tested against the general Wick tensor).
- Attempt 2, fixed now, before evaluation, and applied to every channel (incl. the blinded
  R-hadrons): (i) plateau-onset rule — t_min per channel is the first t such that
  |m_eff(t) − m_eff(t+2)| < σ for two consecutive t, from the jackknife effective mass; windows
  start at or after it; (ii) full 101-config M3 set.  Static-light P₊ (j = 3/2) needs a
  covariant-derivative operator: not tested by this gate, to be added before M4 conclusions.
- If attempt 2 fails, this is reported to the originating session (two honest attempts).
