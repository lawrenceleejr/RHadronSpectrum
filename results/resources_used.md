# Resources used so far (as of 2026-11-27 ~07:30 UTC)

Source: `condor_history` (4,421 finished jobs since 2026-11-21 02:55 UTC) plus the live queue (86 jobs).
Running jobs count their elapsed wall time so far. GPU-h = RemoteWallClockTime × RequestGPUs.
This includes evicted or restarted attempts, so it is the OSPool slot cost, not just useful work.

| Stage / ensemble | Task | Jobs | GPU-h |
|---|---|---:|---:|
| M0 / tests | Benchmarks (gen, solver, HMC), smoke test, toy DAG | 30 | 19.9 |
| qA57 (β=5.7, 12³×24) | Gauge gen + fused R-glueball meas. | 20 | 33.9 |
| | R-glueball re-measurement (enlarged basis) | 42 | 16.5 |
| qA60 (β=6.0, 24³×48) | Gauge gen + fused R-glueball meas. | 40 | 134.1 |
| | Quark propagator solves | 1596 | 356.0 |
| | Nucleon/baryon cross-check solves | 494 | 97.7 |
| | Static-light P-wave solves | 141 | 30.7 |
| | Contractions | 514 | 87.5 |
| | R-glueball re-measurement | 35 | 67.9 |
| qA62 (β=6.2, 32³×64) | Gauge gen + fused R-glueball meas. | 165 | 1194.0 |
| | Quark propagator solves | 1304 | 375.1 |
| | Contractions | 97 | 21.1 |
| | R-glueball re-measurement | 11 | 6.9 |
| dB700 (N_f=2+1, m_π≈700 MeV) | HMC | 8 | 11.6 |
| dB570 (N_f=2+1, m_π≈570 MeV) | HMC | 7 | 10.6 |
| **Total GPU** | | **4504** | **≈2,464** |
| Visuals | Blender renders (CPU) | 3 | 4.2 CPU core-h |

By stage: tests 20 GPU-h (1%), quenched β=5.7 50 (2%), β=6.0 774 (31%), β=6.2 1,597 (65%), dynamical Stage B 22 (1%).
That is **≈12% of the 20,000 GPU-h ceiling**. Most of the remaining budget is for Stage B and Stage C HMC.

## Storage

| Location | Size | Contents |
|---|---:|---|
| OSDF `…/futurecolliders/llee/rhadron/configs` | 258 GB | gauge configs + HMC checkpoints (persistent) |
| OSDF `…/rhadron/images` | 16 GB | Apptainer images |
| `~/rhadron_persist` | 2.9 GB | correlators, blind secret, renders, refs, DAGs/logs |
| `~/RHadronSpectrum` (git) | 9 MB | code, logbook, results, figures |
| `/scratch/llee/rhadron` | 283 GB | working copy (not relied on) |
