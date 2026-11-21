# GPU budget (OSPool, opportunistic)

Ceiling delegated by the user: ~20,000 GPU-h for Stages A + B.  Numbers below are *measured*
(benchmark jobs 43199466, V100-class GPUs, image rhadron-gen-v2, code 285b266) unless marked "est.".

## Stage A — quenched generation + gluelump measurement (CuPy, no solves)

| ensemble | lattice | s / compound sweep (1 HB + 4 OR) | s / gluelump meas. (HYP2+HYP1) | GPU mem |
|---|---|---|---|---|
| qA57 β=5.7 | 12³×24 | 0.33 | 23 | 0.3 GB |
| qA60 β=6.0 | 24³×48 | 3.27 | 97 | 3.6 GB |
| qA62 β=6.2 | 32³×64 | 10.2 | 382 | 12.6 GB |

Plan per ensemble (streams × cfgs, thermalisation, separation) and cost:

| ensemble | streams × cfgs | n_therm | n_sep | sweeps total | GPU-h (gen + meas.) |
|---|---|---|---|---|---|
| qA57 | 10 × 100 | 300 | 20 | 22,800 | 2.1 + 4.8 ≈ 7 |
| qA60 | 10 × 60 | 500 | 30 | 22,700 | 20.6 + 12 ≈ 33 |
| qA62 | 16 × 32 | 700 | 40 | 31,000 | 88 + 40 ≈ 130 |
| **Stage A gauge + gluelumps** | | | | | **≈ 170** |

(Measurement cost averaged with HYP1 on every 4th configuration.)  Heterogeneous GPUs: assume ×2
for slower cards → budget 350 GPU-h.

Measured reality (2026-11-21): many OSPool GPUs are low-FP64 (A40/3090/L40); first segments ran
3-5x slower than the V100 benchmark.  Generation now restricted to V100/A100/H100.  Worst case
Stage A gauge + gluelumps ~700 GPU-h.

## Stage A — quark measurements (M3, M4)

Solver benchmark (cluster 43207478, A40, 24³×48, NP clover c_SW = 1.769, tol 1e-9, one Wuppertal
source = 12 solves):

| κ | method | setup | steady s/solve | iterations |
|---|---|---|---|---|
| 0.13344 | QUDA MG (2 levels, 4⁴ + 2⁴) | 277 s | 0.37 | 12 (GCR) |
| 0.13344 | mixed BiCGStab (double/half) | 33 s | 0.54 | 178 |
| 0.13455 | QUDA MG | 375 s | 0.57 | 15 |
| 0.13455 | mixed BiCGStab | 33 s | 1.24 | 434 |

Choice for β = 6.0: BiCGStab (MG setup not amortised over 16 sources per κ).  Per configuration:
4 κ × 8 sources × 2 source smearings × 12 = 768 solves ≈ 10-12 min + fixed overhead (~7 min,
being profiled) + contractions → ≈ 0.35 GPU-h / config.
- qA60: 600 cfgs → ~210 GPU-h;  qA62 (32³×64, ~3x per config) 512 cfgs → ~550 GPU-h.
- Stage A quark total ≈ 800 GPU-h (×1.5 for slow GPUs / evictions ≈ 1200 GPU-h).

## Stage B — dynamical N_f = 2+1 (self-generated, PACS-CS parameters, 24³×48), estimate

- HMC (PyQUDA: Iwasaki gauge + 2-flavour clover + 1-flavour RHMC clover), est. 5-10 GPU-min per
  trajectory on A100/H100: 2 ensembles × (1000 thermalisation + 400 cfgs × 10) ≈ 10,000
  trajectories ≈ 800-1700 GPU-h.  To be benchmarked at the start of M5.
- Measurements at κ_ud = 0.13700/0.13727 (MG pays off at lighter masses), plus I=0 loops:
  ≈ 800 cfgs × 0.75 GPU-h ≈ 600 GPU-h.
- Stage B total ≈ 1500-2500 GPU-h.

## Total (A + B)

≈ 3,500-4,500 GPU-h including a 1.5x contingency, well under the delegated 20,000 GPU-h ceiling.
**M0 budget gate: passed (delegated ceiling).**  Re-check after the Stage B HMC benchmark.
