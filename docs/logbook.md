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
  (iii) maximal fit time t_max: nucleon 12 → 16, ρ 14 → 16 (π 18, static-light 10 unchanged);
  windows are additionally cut where the correlator is consistent with zero at 2σ.
- Static-light P₊ (pre-registered before any P₊ data): derivative operators (P₋: Σ γ_i D_i;
  P₊: E irrep γ_x D_x − γ_y D_y + cyclic), derivative sources for the strange-like κ_s = 0.13400 only;
  gate comparison P₊ − S (and P₋ − S) at κ_s vs BGR 0809.1103 continuum quenched static-strange
  400(8)(8) MeV (P₊) and 412(10)(8) MeV (P₋), within 2σ, same plateau-onset fit rule, r0 = 0.5 fm.

## 2026-11-22 — M3 gate, attempt 2: FAILED (nucleon only) — reported to the originating session

Full M3 set: 105 qA60 configs (quark), 141 (static-light P-wave at κ_s).  Pre-registered method
(plateau-onset rule, t_max N 16 / ρ 16).  Fixes made during evaluation (bugs, not physics choices):
(a) fitter: positive amplitudes (ln A) and 5 % covariance shrinkage — a fit had diverged to A = −114,
aE = 1.51 on a covariance with condition number 3e11; (b) sign convention of the derivative
static-light correlators (overall minus from the anti-Hermitian symmetric derivative).
Data-quality finding: configuration (stream 8, cfg 0) is **exceptional** at κ = 0.13455 (pion
C(10) = 1.0e4 × median) — the known quenched-clover near-zero-mode artefact; it removes the lightest
pion and static-light fits.  Proposed objective rule (not yet adopted, decision requested):
exclude a configuration from the quenched valence analysis if its pion C(10) exceeds 10× the median
at any κ (applied identically to all channels incl. R-hadrons).

Results (results/qA60_M3_attempt2.json; *_excl.json with the proposed rule):
- π, ρ: all κ within 1.2σ of UKQCD (with exclusion; κ=0.13455 π: 0.2462(25) vs 0.2457).
- Static-light: P₋ − S chiral 435(62) MeV (pull 0.00; 0.70 with exclusion) vs BGR 435(17);
  at κ_s: P₋(deriv) − S = 421(27) vs 412(13) (pull +0.32), P₊ − S = 441(19) vs 400(11) (pull +1.89).
  Heavy-spin partners exactly degenerate.
- Nucleon: a m_N = 0.886(14), 0.777(12), 0.710(20) vs UKQCD 0.799, 0.700, 0.641: pulls +5.2, +4.0,
  +2.45 (with exclusion) → **gate fails**.  The plateau-onset rule fires at t = 6 because the
  effective-mass drift (≈0.05 over t = 4–13) is below the per-step noise; m_eff(t = 9–13) ≈ 0.84–0.88
  for κ = 0.13344 is still above 0.799.  Most likely cause: excited-state contamination of the
  smeared-source / point-sink nucleon (no smeared sink, no GEVP for baryons).
Status: M4 not started.  Stage A generation continues.  Proposed next step (awaiting decision):
smeared-smeared nucleon 2×2 GEVP (sink smearing on all timeslices in the solve job), re-evaluate.

## 2026-11-22 — User decisions on the M3 failure (in this session)

- The report could not be delivered to the originating session (trusted-device refusal); it was
  given to the user directly, who approved both recommendations:
  1. **Exceptional-configuration rule adopted** for all quenched valence analyses (all channels,
     incl. R-hadrons): exclude a configuration if its pion C(10) exceeds 10× the median at any κ.
  2. **Nucleon re-measurement**: smeared-source × smeared-sink 2×2 nucleon matrix (2 Wuppertal levels
     at both ends) on the same 105 configs for κ = l1, l2, l3; M3 gate attempt 3 uses the GEVP
     principal correlator of that matrix with the same plateau-onset rule and t_max = 16 (fixed now).
- Gluelump analyses redone with the fixed fitter (ln A, 5 % shrinkage), bin 4, HYP2:
  r0 (Λ̄(1⁻⁻) − Λ̄(1⁺⁻)) = 1.130(81) at β = 5.7 (1000 cfgs), 0.972(138) at β = 6.0 (600 cfgs, generation
  complete).  Literature continuum 0.87(9) (HSW), 0.933(18) (FM).  M2 gate awaits β = 6.2.
- Nucleon-matrix DAG 43223267 running (315 jobs, ~7 min each).

## 2026-11-23 — M3 gate, attempt 3: FAILED (nucleon); excited-state hypothesis not supported

- Smeared×smeared 2×2 nucleon GEVP (104 cfgs after exceptional exclusion; DAG 43223267 + rescue).
  a m_N = 0.856(7), 0.753(6), 0.687(9) vs UKQCD 0.799, 0.700, 0.641 (QCDSF interpolates to ≈0.80,
  0.71): pulls +4.6, +3.3, +2.1.  Effective mass of the principal correlator is FLAT: 0.84–0.86 for
  t = 4–12 (κ = 0.13344), ≈0.69 for t = 4–10 (κ = 0.13455).  A persistent ~7 % excess, nucleon only;
  π, ρ (all κ), static-light S/P₋/P₊ agree.  The flat plateau does not look like excited-state
  contamination; a baryon-specific systematic or bug is not excluded (existing checks: fast nucleon ==
  general Wick tensor at a site; colour-singlet SU(6) 56 Pauli pattern; operator ε(uᵀCγ5d)P₊u, C = γ_yγ_t).
  Note a m_Δ at κ = 0.13344 is expected ≈ 0.87, uncomfortably close to our 0.856.
- Blackwell (cc 12.0) GPUs excluded everywhere: no sm_120 CuPy kernels in the CUDA 12.4 images.
- Reported to the user; M4 not started.

## 2026-11-23 — Nucleon investigation (user: "keep going until trustworthy")

- Free-field check: forward propagation ∝ (1+γ4)/2 in our convention (parity projector correct).
- New independent site-vectorised general baryon contraction (`light.baryon_corr`), == fast nucleon.
- Cross-check measurement on 40 qA60 configs, κ = 0.13344 (largest discrepancy): 2×2 smeared
  matrices for N1 (Cγ5, both code paths), N2 (Cγ4γ5) and Δ⁺⁺ (Cγ_k, spin-3/2 projected).
  Decision criteria (fixed now): N1 and N2 ground states must agree; m_Δ − m_N must be clearly
  positive (expected a(m_Δ − m_N) ≈ 0.07 at m_π ≈ 840 MeV).  If our "N" ≈ our Δ → operator/
  contraction problem; if N1 ≈ N2 < Δ with the 7 % excess intact → treat as a genuine
  method/systematic difference and investigate the comparison (volume, fit, smearing) instead.

## 2026-11-23 — ROOT CAUSE FOUND: antiperiodic-boundary sign of wrapped quark propagators

- UKQCD Table VI verified directly from the PDF text (hep-lat/9910022v3): a m_N = 0.799/0.700/0.641,
  a m_Δ = 0.899/0.818/0.781 (32³×64, β = 6.0 NP).
- Diagnosis: per-source nucleon correlators flip sign exactly at t = L_t − t0.  QUDA uses antiperiodic
  temporal BCs (t_boundary = −1), so a propagator wrapping past t = L_t carries (−1); contractions were
  written for unwrapped propagators.  Mesons (2 lines) are unaffected (why π, ρ agreed); baryons
  (3 lines) and static-light / R-baryons (odd number of light lines) were biased: wrapped sources
  subtract at late t → effective masses too high.  Gluelumps and R-mesons unaffected.
- Fix (`rhadron/apbc.py`): every extracted propagator multiplied by (−1)^(boundary crossings);
  new outputs carry `apbc_unwrapped = 1`; legacy per-source files corrected in the analysis /
  re-contraction.  Test: translation invariance (wrapped source vs time-shifted configuration) for
  site series, nucleon, static-light, pion.
- Check on the attempt-3 nucleon matrices with the correction: a m_N = 0.7886(33), 0.6814(38),
  0.6207(85) vs UKQCD 0.799, 0.700, 0.641 — clean plateaus, pulls −0.7, −1.2, −1.2.
- quark.h5 regenerated from the per-source propagator files (contract-only DAG 43233038; old files in
  quark/pre_apbc_fix/).  M3 to be re-evaluated with the unchanged pre-registered method.
- Lesson recorded: three gate failures were one bug; the excited-state diagnosis of attempts 1-2 was
  wrong.  Test added so this cannot recur.

## 2026-11-23 — M3 GATE PASSED (after the APBC fix)

results/qA60_M3_attempt4.json — 105 qA60 configs (1 exceptional excluded), unchanged pre-registered
method (plateau-onset rule; nucleon from the smeared×smeared GEVP), re-contracted with APBC signs:
- π: 0.3972(8), 0.3050(11), 0.2462(25) vs 0.3952, 0.3048, 0.2457 (pulls +1.1, +0.1, +0.2)
- ρ: 0.5370(23), 0.4815(39), 0.4620(70) vs 0.5400, 0.4887, 0.4636 (pulls −0.6, −1.0, −0.1)
- N: 0.7886(33), 0.6814(38), 0.6207(85) vs 0.799, 0.700, 0.641 (pulls −1.0, −1.2, −0.9)
- Static-light P₋ − S chiral 459(24) MeV vs BGR 435(17) (pull +0.8); at κ_s P₋(deriv) − S = 406(19)
  vs 412 (−0.3), P₊ − S = 438(21) vs 400 (+1.6); heavy-spin partners exactly degenerate.
Proceeding to M4 (quenched R-mesons and R-baryons; blinded).

## 2026-11-23 — M4 checks on production data; analysis choices frozen (blinded)

- GPU vs CPU-reference gate item (qA60_s0_c0004, real propagators): full GPU contraction == NumPy
  re-contraction, 226 datasets, max rel. diff 3.7e-16; R-meson (us, γ5) production == explicit-loop
  reference 4e-19; R-baryon (uds singlet, octet_A) production == reference 3.7e-15.  **Passed.**
- Blinded dry run (results/qA60_M4_blinded_dryrun.json, 104 cfgs, 188 channels): equivalent-operator
  pairs (γ5/γ4γ5, γ_i/γ4γ_i, 1/γ4, γ5γ_i/γ4γ5γ_i) agree within 2σ in 35/35 cases; Im C consistent
  with zero (median of per-channel max 2.0σ over 28 tests); Hermiticity of the 2×2 smearing matrices
  median of max 2.9σ (ensemble-average property, acceptable); HYP1 vs HYP2 splittings agree
  (10 well-measured channels: mean pull 0.26, max |pull| 0.42).
- Frozen before unblinding: (i) fit method as M3 (GEVP t0 = 1, td = 2, plateau-onset rule, AIC,
  bin 2, exceptional-config rule); (ii) per J^P and flavour, the operator of the equivalent pair with
  the smaller total error is used (decided on blinded data); (iii) headline splittings HYP2;
  HYP1 − HYP2 difference enters the systematic budget; (iv) unblinding once, when qA60 has 300 cfgs
  (every 2nd) and qA62 ≥ 80 cfgs of quark data.

## 2026-11-24 — Naming and new deliverable

- Naming convention (user): "R-glueball" for g̃g states in prose/figures/paper; "gluelump" only as the
  lattice term for the static-limit object (CLAUDE.md updated; figures relabelled).
- New deliverable docs/fragmentation.md: fraction of gluinos ending in R-glueballs — not a lattice
  observable (fragmentation); lattice supplies spectrum/thresholds, R-glueball–I=0 R-meson mixing (M5)
  and inputs for a Pythia 8 R-hadron study with the gluinoball probability as a model parameter.
- BESIII X(2370) (0⁻⁺ glueball-dominated claim, 2025-2026): ordinary glueballs; no direct effect on
  R-glueball/R-hadron spectroscopy here (different system, colour-octet static source).  Indirect
  relevance only (see summary to user).
- 2026-11-24: qA62 generation (critical path for M2 and M4) starved of ≥15 GB GPUs (2 running, 41 matching
  slots busy).  qA62 gen priority raised to 10; qA62 quark DAG halted (new submissions paused) until
  generation catches up.  qA60 quark (11 GB GPUs) continues.
- 2026-11-24: qA62 quark measurements switched from every 2nd to every configuration (n_sep = 40
  compound sweeps; binning studies flat at β = 5.7/6.0) so the pre-registered M4 unblinding condition
  (qA62 ≥ 80 quark cfgs) can be met from the 97 existing configs; gen keeps priority 10 > quark 5.
  qA62 gen disk request lowered 20 → 10 GB.

## 2026-11-25 — Baryon cross-check complete: baryon code validated

κ = 0.13344, 104 qA60 configs, smeared×smeared GEVP, APBC-corrected:
N1 (Cγ5, production) = N1 (independent general-Wick path) = 0.7886(33); N2 (Cγ4γ5) = 0.7899(32);
Δ⁺⁺ = 0.8825(43) vs UKQCD 0.899 (pull −1.1); a(M_Δ − M_N) = 0.0939(26) vs UKQCD 0.100.
Two interpolators agree, two code paths agree, N and Δ correctly separated, both match the literature:
the shared baryon machinery (used for the R-baryons) is validated.
- qA60 quark DAG ended with one failed node (299/300); rescue DAG resubmitted.
- 2026-11-26: qA62 quark DAG 43248796 stopped (106 failed solve nodes, 64 futile contracts; 250 done):
  CuPy OutOfMemory on 16–24 GB GPUs (32³×64 propagator = 4.8 GB complex128, pool caching).  Fix: free
  the CuPy pool after each source; qA62 solves require GPUs ≥ 40 GB.  Rescue DAG 43273517.
- 2026-11-26: qA62 rescue: no new OOMs with ≥ 40 GB GPUs but only 1 such slot at a time.  The memory
  hog was the zero-momentum light-hadron einsums on the full 32³×64 propagator (several 4.8 GB
  intermediates), needed only for M3 (passed at β = 6.0).  `light_hadrons: false` for qA62; solves
  now accept ≥ 20 GB GPUs (idle jobs edited; DAG code/ens refreshed).

## 2026-11-26 — M4 UNBLINDING (performed once)

- Conditions met: qA60 300 quark cfgs, qA62 89 quark cfgs (≥ 80).  All gluelump files fixed-basis
  (qA60 600, qA62 385).  Analysis choices as frozen on 2026-11-23 (logbook).  Code 27a02bc.
- Run: `python -m rhadron.analysis.m4 <tag> <quark/out> results/<tag>_M4_unblinded.json --UNBLIND`
  for qA60 and qA62, started 20:59Z.
- M4 unblinded results: results/qA60_M4_unblinded.json (293 cfgs), results/qA62_M4_unblinded.json
  (89 cfgs), summary results/M4_review.md.  β = 6.0: R-glueball (1⁺⁻) lightest at all κ; 1⁻/0⁻
  R-mesons +0.5 r0 (≈200 MeV) above at heavy κ, 1⁻ +0.19(13) r0 at the lightest κ; R-baryons ≥ +1.4 r0
  (S⁰ lightest R-baryon).  β = 6.2: R-meson fits on late noise windows (t = 12–18) → undetermined;
  FLAGGED.  Proposed: quark measurements on all ~380 qA62 configs; t_max signal-to-noise cut
  (post-unblinding change, documented).

## 2026-11-27 — User: proceed with both (β = 6.2 completion and Stage B)

- Post-unblinding analysis change (documented as such): the plateau-onset rule fires on noise when
  σ is large (|m(t) − m(t+2)| < σ trivially satisfied at late t), which pushed β = 6.2 fits to
  t = 12–18.  New rule for all channels and both spacings: t_max = last t with C/σ ≥ 4; the onset is
  searched below that and capped at t_max − 3.  The rule depends only on signal-to-noise, not on any
  reference value.  M3 and M4 results are re-evaluated with it (both reported).
- Stage B (M5) started (user approval 2026-11-27): HMC DAGs dB700 43306882 and dB570 43306883,
  4 streams × (500 thermalisation + 100 cfgs × 10 traj), τ = 0.5, Omelyan 12×5, V100/A100/H100.
  Fixes before launch: per-stream RNG seeds; per-segment HMC logs.  Quark settings added (unitary κ,
  paired sources, densities on); MG vs BiCGStab to be benchmarked on the first configurations.
- qA62 quark production on all remaining 299 configs: DAG 43306865.

## 2026-11-27 — Precision programme started (docs/precision_plan.md)

User asked for a solid physical prediction with reduced errors → Stage C approved.  Launched:
qA60 quark on remaining 300 cfgs (n_src 16, cross-correlators) DAG 43306995; qA60 re-contraction with
cross-correlators 43306996 (old quark.h5 in quark/pre_cross/); enlarged R-glueball basis
re-measurement qA57 43307026, qA60 43307027, qA62 43307028 (≥ 40 GB GPUs); qA62 gen now --no-measure;
Stage C HMC benchmarks dB410 / dB300 (43307054); literature lookup for the second dynamical spacing.
- Second dynamical spacing chosen (docs/stageC_parameters.md): CP-PACS/JLQCD β = 2.05, c_SW = 1.628,
  a ≈ 0.070 fm, 32³×64 (L ≈ 2.24 fm), same action as β = 1.90 (Iwasaki + unsmeared NP clover).
  Ensembles dC56 (κ_ud 0.13560, κ_s 0.13510; published point, r0/a = 7.06 from WHOT-QCD) and
  dC54 (κ_ud 0.13540, κ_s 0.13510).  Pion masses to be measured; combined fit in (m_π, a) does not
  need exact matching.  PACS10 (stout-smeared clover) excluded: different action.  Scale: one common
  quantity (r0 / w0 / t0 from our own measurements) at both β.

## 2026-11-27 — Effect of the S/N t_max cut at β = 6.0; Stage B HMC cost

- M3 re-run with the cut (results/qA60_M3_sncut.json): still passes; all π, ρ, N within 1.2σ of UKQCD.
- M4 qA60 re-run (results/qA60_M4_unblinded_sncut.json): R-glueball aE 0.7670(215) → 0.7686(43)
  (error 5× smaller: noise-only windows had entered the AIC spread); 94 HYP2 splittings: median
  error 0.163 → 0.099 r0, median shift −0.012 r0 (max |shift| 0.154 r0).  Central values stable; the
  cut adopted for all further analysis.
- Stage B HMC (V100): 340 s/trajectory after thermalisation onset (CG iterations grow away from the
  cold start; benchmark 38–72 s was from the cold start).  Acceptance 65 % (dB700), 57 % (dB570) with
  12 outer steps → raised to 14 / 16.  Revised Stage B estimate ≈ 1,500 GPU-h; Stage C (32³×64) to be
  re-estimated from benchmarks; budget to be re-checked against the 20k ceiling (report if exceeded).
- 2026-11-27: Big-GPU starvation: only ~35 FP64-class (V100/A100/H100) ≥15 GB GPUs in the pool, mostly
  claimed by others; our fair-share effective priority 42,600 after ~47k slot-h.  Stage B HMC and Stage C
  benchmarks opened to any cc 7.0–9.x ≥15 GB GPU (sloppy-precision CG dominates); HMC host memory 4 GB;
  holds for the 20 h execute limit (code 47) auto-released (checkpoint every trajectory).

## 2026-11-27 — Stage C budget check (before any Stage C production)
- dB300 cold benchmark (43307054.1) died: QUDA OOM on a 24 GB Quadro RTX 6000 (32³×64 RHMC, double/single).
  Resubmitted alone requiring ≥ 39 GB GPU memory (cluster 43322539).
- dB410 cold benchmark (43307054.0) is running on a V100.  Cold-start benchmarks underestimated Stage B
  ~4× (90 s predicted vs 340 s/traj measured), so a warm-start dB410 benchmark from dB570 s1 traj 40
  (cluster 43322754, 12 traj) was added to get a near-equilibrium s/traj.
- Stage B segments 0-40: dB700 332-349 s/traj on V100 (88 s on one fast card), acceptance 0.57-0.60
  (n_outer 12); dB570 309-342 s/traj, acceptance 0.43-0.50.  Segments from traj 40 (n_outer 14/16) are queued.
- Projection (scaling with CG cost ∝ 1/m_q (κ_c ≈ 0.13781), step count and volume; plan 4 streams ×
  (500 + 1000) traj each):  spent 2,464; Stage A remaining ≈ 1,100; Stage B ≈ 1,900 (HMC + meas.);
  dB410 ≈ 2,000; dB300 ≈ 9,100; β = 2.05 pair ≈ 6,300  →  ≈ 23,000 GPU-h > 20,000 ceiling.
  dB300 also needs ≈ 1500 traj × ~5000 s (A100) ≈ 3 months per stream: not feasible in wall-clock.
  Without dB300: ≈ 13,800.  Reported to the user with options; no Stage C production launched.

## 2026-11-27 — Stage C decision (user: "do what you recommend" → option A now, B if access)
- dB300 dropped from our own generation (benchmark 43322539 removed).  Chiral lever arm 700/570/410 MeV.
  Projection ≈ 13,800 GPU-h.  If dB410 measures far above ~1,000 s/traj (V100), dC54 is dropped too.
- dB410 production DAG submitted (cluster 43322772): 4 streams × (500 + 100×10) traj, segments of 40,
  cold start, n_outer 16 (to be retuned per segment from the warm benchmark 43322754, as in Stage B).
- dC56/dC54 cold benchmarks submitted (cluster 43322779, ≥ 30 GB GPUs, 12 traj).
- Option B: PACS-CS N_f=2+1 β=1.90 32³×64 ensembles (Iwasaki + NP clover, c_SW 1.715; κ_ud down to
  0.13781, m_π ≈ 156 MeV) are distributed through ILDG/JLDG.  Access needs an ILDG account (INDIGO IAM at
  iam-ildg.cloud.cnaf.infn.it; token-based gfal/curl downloads) — the user has to register; ~1.2 GB per
  config in double precision.  Same action/parameters as our dB* ensembles, so they would slot in as
  dB410/dB300 (and the physical point) at larger volume.

## 2026-11-27 (afternoon) — Stage C check-in
- dB410 cold benchmark (V100-PCIe-32GB): 12/12 accepted at n_outer 16, s/traj rising 266 → 418 (not yet
  saturated; dH rising to 0.1-0.25).  Stage B cold runs saturated near 340 s on V100; dB410 equilibrium
  expected ~600-900 s/traj (< 1000), so dC54 is kept for now.  Projection unchanged ≈ 13,800 GPU-h.
- Warm-start dB410 benchmark (43322754) and dC56/dC54 benchmarks (43322779) have not started yet.
- Stage B: segments from traj 40 still idle (~9 h); only 6 slots matched.  HMC peak device memory is
  8.7 GB (24³×48), so the GPU floor for dB700/dB570/dB410 was lowered from 15 GB to 10 GB (adds RTX 2080 Ti;
  same FP64 class as the already-allowed Quadro RTX 6000), via condor_qedit (expression, not string) and in
  each DAG's hmc.sub.  Real bottleneck is fair share (effective priority 39,300 after ~47.5k slot-h).

## 2026-11-27 (evening) — HMC GPU class matters 10×
- Stage B segments from traj 40 that ran on GeForce RTX 3060 (12 GB) took 3,690-4,020 s per trajectory
  (V100 ≈ 340 s, H100 ≈ 88 s): the RHMC force/outer solves are double precision and consumer cards
  have 1/64-rate FP64.  Each such job finished one trajectory before eviction.
- The 10 GB floor set this afternoon would have admitted exactly these cards.  Reverted: HMC now requires
  cc 7.0/8.0/9.0 (V100/A100/H100) with ≥ 15 GB — condor_qedit on the 12 queued jobs (expression),
  the three hmc.sub files (repaired with python after sed '&' mangling), and the manifest hmc default.
  dB700 s3 and dB410 s0 were vacated off RTX 3060s (resume from checkpoint).
- Acceptance at n_outer 14/16 not yet measurable (one trajectory per stream so far).
- Warm dB410 and dC56/dC54 benchmarks still idle; Stage C projection unchanged (≈ 13,800 GPU-h).

## 2026-11-28 00:40 — Stage C benchmarks, Stage B acceptance, HMC diagnostic
- Warm dB410 benchmark (V100-SXM2-16GB, from dB570 s1 traj 40, n_outer 16): 462-484 s/traj, acceptance
  5/12, <dH> ≈ 1.1.  n_outer → 20 for later dB410 segments (dH ∝ h⁴ → ×0.41; cost ×1.25 ≈ 590 s/traj).
  dB410 HMC ≈ 6000 × 590 s ≈ 1,000 V100-h (earlier estimate 1,700): dC54 is kept.
- dC56/dC54 benchmarks (32³×64): QUDA OOM on V100-32GB (24³×48 peaks at 8.7 GB; ×3.16 volume).
  Resubmitted requiring ≥ 39 GB (cluster 43383382).  β = 2.05 production will need A100/H100 only.
- All HMC segments now on V100/A100/H100 (RequireGPUs expression verified on the 12 queued jobs).
- Stage B from traj 40 (n_outer 14/16): acceptance did NOT improve (dB700 0.56 → 0.36, dB570 0.45 → 0.43;
  mean dH 0.8-2.1).  Plaquette still drifting down (0.5725 → 0.5710): still thermalising.
  dB570 s2 traj 73-77: five rejections in a row from one configuration, dH = 30, 10, 10266, 1, 5.
  Light pair is an exact 2-flavour pseudofermion (no rational approximation; the strange x^{1/4}
  approximation on [7e-4, 32] acts on the heavier strange operator), so suspicion falls on the light CG:
  Stage B had maxiter 5000 with QUDA output silenced, so an unconverged action solve would be invisible.
  maxiter → 20000 for later Stage B segments; added hmc.verbose (QUDA_SUMMARIZE) and submitted a
  diagnostic replay from dB570 s2 traj 80 with maxiter 5000 + verbose (cluster 43383484, 6 traj).
  No measured configurations affected: all streams are within n_therm = 500.
- HMC logged so far: 643 trajectories, 48.8 GPU-h.  Stage C projection ≈ 13,000 GPU-h total.

## 2026-11-28 06:00 — HMC diagnostic result; β = 2.05 launched
- Diagnostic replay (43383484, V100, dB570 s2 traj 80→86, maxiter 5000, QUDA SUMMARIZE): no solve near
  maxiter (light CG ≤ ~1,760 iterations; MultiShift ~500); no warnings.  Yet dH = 40, 56, 5.8, 5.5, 5.3,
  1.7 from the same configuration.  Unconverged solves are ruled out.
- QUDA κ-normalised even-even asymmetric MATPC: M†M spectrum well inside the strange rational range
  [7e-4, 32], so the approximation range is not the suspect either.
- Next test (cluster 43395412): dH split into dK/dSg/dSf (new log fields) and three replays with identical
  seeds — base (16×5), n_outer 32, n_inner 10.  Integration error should drop ~16× when the relevant step
  is halved; a dH that stays put points to an action/force inconsistency.
- Stage B/dB410 now (last 20 traj): dB700 acc 0.35-0.50 (mean dH 0.8-1.6); dB570 0.10-0.45 (mean dH 2.4-6.8,
  7 spikes dH > 10 on s2); dB410 0.40-0.70.  Thermalisation trajectories only (≤ traj 120 of 500).
- dC56 (H100) / dC54 (A100) cold benchmarks: 12 traj each, 285 → 298 s and 476 → 530 s per trajectory,
  acceptance 7/12 and 11/12; 27.6 GB device, 4.7 GB host memory.  Production DAGs submitted
  (43395415, 43395416): A100/H100 ≥ 39 GB, 8 GB memory, 15 GB disk, n_outer 20.
- Projection: β = 2.05 ≈ 2 × 6000 × ~700 s ≈ 2,300 GPU-h HMC (+ ~1,600 meas.) — below the 6,300 estimate.
  Total ≈ 11,000-12,000 GPU-h.

## 2026-11-28 08:45 — HMC dH diagnosis concluded: outer (fermion) step too large
Replays from dB570 s2 traj 80, identical seeds, 4 trajectories each (V100):
| variant        | dH (traj 81-84)              | accepted |
|----------------|------------------------------|----------|
| 16 × 5 (prod.) | 39.8, 55.5, 5.80, 5.51       | 0/4      |
| 32 × 5         | -0.41, -0.08, -0.10, 0.32    | 4/4      |
| 16 × 10        | identical to 16 × 5 (< 1e-3) | 0/4      |
- Halving the outer step reduces |dH| 15-100× (≥ the h⁴ factor 16): fermion-force integration error near
  its stability threshold at n_outer 16, not an action/force inconsistency.  The inner (gauge) integration
  is already converged (n_inner 5 vs 10 agree to < 1e-3); dSg ~ 10³ is the physical change along the
  trajectory, cancelled by dK and dSf.
- New n_outer for later segments (dH ∝ h⁴, target mean dH ≈ 0.3): dB700 14 → 20, dB570 16 → 28,
  dB410 20 → 28.  β = 2.05 stays at 20 until warm data.  Running segments finish with the old values;
  all affected trajectories are thermalisation (≤ traj ~130 of 500).
- Hasenbusch mass preconditioning would be cheaper but PyQUDA has no ratio monomial (new code +
  validation); deferred.
- Cost: Stage B HMC ≈ 1,800 V100-h (was 1,300), dB410 ≈ 1,400 (was 1,000).  Higher acceptance shortens
  autocorrelations, partly compensating.  Total projection ≈ 12,000-13,000 GPU-h.
