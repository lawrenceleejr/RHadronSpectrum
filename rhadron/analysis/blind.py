"""Blinding of the R-hadron vs gluelump ordering (CLAUDE.md): until unblinding, every quark-sector
(R-meson / R-baryon) energy is shifted by a secret offset in lattice units, drawn per ensemble
from a secret stored outside the repository.  Fit ranges and operator bases are frozen on blinded
data; `unblind` is called exactly once per ensemble and logged."""
import hashlib
import os

SECRET = os.environ.get("RHADRON_BLIND_SECRET", "/scratch/llee/rhadron/blind/secret")


def offset(tag, scale=0.08):
    """Uniform offset in [-scale, +scale] (lattice units) per ensemble tag."""
    key = open(SECRET).read().strip()
    h = hashlib.sha256((key + tag).encode()).digest()
    u = int.from_bytes(h[:8], "big") / 2**64
    return (2 * u - 1) * scale
