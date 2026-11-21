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
