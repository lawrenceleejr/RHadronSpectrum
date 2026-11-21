# Final visual deliverable: what the lightest R-hadron "looks like" (user request, 2026-11-21)

Goal: a Blender (Cycles) animation of the lattice-determined spatial structure of the lightest
R-hadron, conveying both the noisy QCD vacuum ("soup") and the smooth averaged bound state.

## Lattice observables (all gauge invariant, static gluino at the origin)

1. **Light-quark cloud** (R-meson / R-baryon):
   ρ_Γ(r) = ⟨O(t1) [q̄Γq](x0 + r, τ) O†(t0)⟩ / ⟨O(t1) O†(t0)⟩ with t0 < τ < t1, Γ = γ4 (charge),
   1 (matter); ground-state dominated for τ − t0, t1 − τ large.  Uses the paired sources
   (`pair_sep` in the ensemble YAML): point-to-all propagators from (x0, t0) and (x0, t1) give both legs
   via γ5-hermiticity.  Computed inside the solve job (both sources of a pair belong to the same job),
   stored as a 3D map on the insertion timeslice τ = t0 + pair_sep/2.  Connected insertions only
   (quenched / I=1 flavour structure); disconnected pieces belong to Stage B.
2. **Glue cloud** (gluelump, and the gluonic part of every state): chromo-electric/magnetic energy
   density E²(x0 + r, τ), B²(x0 + r, τ) from the clover F_μν (flowed links), correlated with the
   ground-state projected correlator, minus the vacuum value.  Gauge fields only; runs as a separate
   job on the stored configurations.
3. **Vacuum foam**: action and topological-charge density of individual configurations after
   gradient flow (Leinweber-style), for the opening sequence.

All maps are averaged over the 48 cubic symmetry operations and over sources/configurations, with
jackknife errors; voxels consistent with zero within 2σ are faded to zero in the render.

## Animation (storyboard)

1. Fly through one flowed configuration: flickering action-density foam (OpenVDB volume per frame).
2. Configuration average builds up: the foam dissolves, a cubically symmetric cloud around the gold
   gluino point remains.
3. Split view / colour channels: quark charge density (blue), chromo-electric (red), chromo-magnetic
   (amber) energy density.
4. Euclidean-time growth: τ slider shows excited-state contamination dying out.
5. Slow orbit with scale bar in fm (r0-based).

Pipeline: densities (HDF5) -> OpenVDB grids via Blender's bundled `openvdb` module -> Blender volume
objects -> Cycles frames rendered as OSPool CPU jobs (one chunk of frames per job) -> ffmpeg.

Prerequisites before M4 production: density contraction in `solve_role` + unit tests (gauge
invariance, cubic covariance, reference contraction on 4³×8).
