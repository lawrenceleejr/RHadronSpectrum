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
