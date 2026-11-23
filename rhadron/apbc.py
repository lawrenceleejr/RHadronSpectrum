"""Antiperiodic temporal boundary conditions for quark propagators (QUDA t_boundary = -1).

A propagator from source time t_src to sink time t_snk, stored on the periodic lattice, equals the
"unwrapped" propagator times (-1)^w, where w is the number of times the straight path from t_src to
t_snk (in unwrapped times) crosses the boundary.  Contractions are written for unwrapped propagators
(source effectively at t = 0), so every extracted propagator is multiplied by this sign.  Mesons are
insensitive (two quark lines), baryons (three) and static-light (one light line) are not.
Found 2026-11-23: the nucleon effective mass was biased high by wrapped sources (docs/logbook.md).
"""
import numpy as np


def sign(t_src_u, t_snk_u, Lt):
    """(-1)^w for unwrapped integer times (may be outside [0, Lt))."""
    du = t_snk_u - t_src_u
    ds = (t_snk_u % Lt) - (t_src_u % Lt)
    w = (du - ds) // Lt
    return -1.0 if (w % 2) else 1.0


def site_series_signs(t0, n, Lt):
    """Signs for a forward site series S(t0 + t; t0), t = 0..n-1."""
    return np.array([sign(t0, t0 + t, Lt) for t in range(n)])
