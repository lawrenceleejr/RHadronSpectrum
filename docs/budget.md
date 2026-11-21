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

## Stage A — quark measurements (M3, M4): QUDA solves  (to be measured once the QUDA image passes M0)

## Stage B — dynamical N_f=2+1 self-generation + measurements (to be measured)
