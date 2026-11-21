"""Gauge-configuration and correlator I/O (HDF5, atomic writes, provenance attributes).

Configurations are stored as the first two rows of each link ("12-real" compression); the third row is
rebuilt as (r0 x r1)^*.  Measurement copies may be single precision (reunitarised on load);
Markov-chain checkpoints are always double precision."""
import hashlib
import json
import os
import subprocess

import h5py
import numpy as np

from .field import reunitarize


def git_sha():
    sha = os.environ.get("RHADRON_GIT_SHA")
    if sha:
        return sha
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        return subprocess.check_output(["git", "-C", here, "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def _atomic(path):
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    return tmp


def save_gauge(path, U, attrs=None, precision="double"):
    U = np.asarray(U)
    rows = U[..., :2, :]
    dt = np.complex128 if precision == "double" else np.complex64
    tmp = _atomic(path)
    with h5py.File(tmp, "w") as f:
        d = f.create_dataset("U2", data=rows.astype(dt))
        d.attrs["layout"] = "U[mu,t,z,y,x,row(2),col(3)], mu=x,y,z,t"
        for k, v in (attrs or {}).items():
            f.attrs[k] = v if not isinstance(v, dict) else json.dumps(v, sort_keys=True)
        f.attrs.setdefault("git_sha", git_sha())
    os.replace(tmp, path)


def load_gauge(path):
    with h5py.File(path, "r") as f:
        rows = f["U2"][...].astype(np.complex128)
        attrs = dict(f.attrs)
    r2 = np.cross(rows[..., 0, :], rows[..., 1, :]).conj()
    U = np.concatenate([rows, r2[..., None, :]], axis=-2)
    return reunitarize(U), attrs


def save_h5(path, groups: dict, attrs=None):
    """groups: {name: ndarray} written as datasets; attrs on the root (atomic)."""
    tmp = _atomic(path)
    with h5py.File(tmp, "w") as f:
        for k, v in groups.items():
            f.create_dataset(k, data=np.asarray(v))
        for k, v in (attrs or {}).items():
            f.attrs[k] = v if not isinstance(v, dict) else json.dumps(v, sort_keys=True)
        if "git_sha" not in f.attrs:
            f.attrs["git_sha"] = git_sha()
    os.replace(tmp, path)
