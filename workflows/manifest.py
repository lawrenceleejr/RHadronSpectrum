"""Generate DAGMan workflows (DAG + per-node VARS) from ensemble YAMLs.

    python workflows/manifest.py gen configs/ensembles/qA60.yaml --streams 10 --segment 200 --image osdf://...

Each stream is a linear chain of `gen` segments (each `--until` an absolute sweep count), so a rescue
DAG resumes exactly; segments whose checkpoint already shows the target sweep are marked DONE.
Code is shipped as code.tar.gz built from a *committed* git SHA (`git archive`).
"""
import argparse
import os
import shutil
import subprocess
import sys

import h5py
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.environ.get("RHADRON_DATA", "/scratch/llee/rhadron/data")


def code_tarball(dest):
    sha = subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"]).decode().strip()
    dirty = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--", "rhadron"]).returncode
    if dirty:
        sys.exit("rhadron/ has uncommitted changes: commit (and push) before submitting")
    tmp = dest + ".tar"
    subprocess.check_call(["git", "-C", REPO, "archive", "--format=tar", "-o", tmp, sha, "rhadron"])
    d = os.path.dirname(dest)
    with open(os.path.join(d, "GIT_SHA"), "w") as f:
        f.write(sha + "\n")
    subprocess.check_call(["tar", "-rf", tmp, "-C", d, "GIT_SHA"])
    subprocess.check_call(["gzip", "-f", tmp])
    os.replace(tmp + ".gz", dest)
    return sha


def ckpt_sweeps(path):
    try:
        with h5py.File(path, "r") as f:
            return int(f.attrs["sweeps"])
    except Exception:  # noqa: BLE001
        return -1


def gen_dag(a):
    ens = yaml.safe_load(open(a.ensemble))
    tag = ens["tag"]
    base = os.path.join(DATA, tag)
    dagdir = os.path.join(base, "dag")
    os.makedirs(dagdir, exist_ok=True)
    sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
    shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
    shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)
    shutil.copy(os.path.join(HERE, "condor", "gen.sub"), dagdir)
    nsep, ntherm = ens["n_sep"], ens["n_therm"]
    per_stream = -(-ens["target_configs"] // a.streams)
    total = ntherm + nsep * (per_stream - 1)
    lines = [f"# {tag}: {a.streams} streams x {per_stream} cfgs; code {sha}", f"CONFIG {dagdir}/dagman.config"]
    for s in range(a.streams):
        iwd = os.path.join(base, f"s{s}")
        os.makedirs(os.path.join(iwd, "logs"), exist_ok=True)
        ck = os.path.join(iwd, "out", f"{tag}_s{s}_ckpt.h5")
        have = ckpt_sweeps(ck)
        prev = None
        untils = list(range(a.segment, total, a.segment)) + [total]
        for k, u in enumerate(untils):
            node = f"g_s{s}_{k}"
            inputs = [os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml")]
            startarg = ""
            if k > 0 or have > 0:
                inputs.append(ck)
                startarg = f"--start {os.path.basename(ck)}"
            lines.append(f"JOB {node} {dagdir}/gen.sub" + (" DONE" if have >= u else ""))
            lines.append(f'VARS {node} TAG="{tag}" STREAM="{s}" UNTIL="{u}" IWD="{iwd}" '
                         f'INPUTS="{",".join(inputs)}" STARTARG="{startarg}" IMAGE="{a.image}" '
                         f'GPUREQ="{a.gpureq}" MEM="{a.mem}" DISK="{a.disk}"')
            lines.append(f"RETRY {node} 3")
            if prev:
                lines.append(f"PARENT {prev} CHILD {node}")
            prev = node
    with open(os.path.join(dagdir, "dagman.config"), "w") as f:
        f.write(f"DAGMAN_MAX_JOBS_SUBMITTED = {a.maxjobs}\nDAGMAN_MAX_JOBS_IDLE = {a.maxjobs}\n")
    dag = os.path.join(dagdir, f"{tag}_gen.dag")
    with open(dag, "w") as f:
        f.write("\n".join(lines) + "\n")
    # gen.sub reads wrapper.sh relative to initialdir: point executable at the dag copy
    sub = open(os.path.join(dagdir, "gen.sub")).read().replace("executable               = wrapper.sh",
                                                               f"executable               = {dagdir}/wrapper.sh")
    open(os.path.join(dagdir, "gen.sub"), "w").write(sub)
    print(dag)


def refresh_code(a):
    """Rebuild code.tar.gz of an existing DAG (future nodes pick it up; outputs record the SHA)."""
    dagdir = os.path.join(DATA, a.tag, "dag")
    print(code_tarball(os.path.join(dagdir, "code.tar.gz")))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("ensemble")
    g.add_argument("--streams", type=int, required=True)
    g.add_argument("--segment", type=int, required=True, help="compound sweeps per job")
    g.add_argument("--image", required=True)
    g.add_argument("--gpureq", default="(Capability >= 6.0) && (GlobalMemoryMb >= 7000)")
    g.add_argument("--mem", default="8GB")
    g.add_argument("--disk", default="8GB")
    g.add_argument("--maxjobs", type=int, default=40)
    r = sub.add_parser("refresh-code")
    r.add_argument("tag")
    a = p.parse_args()
    {"gen": gen_dag, "refresh-code": refresh_code}[a.cmd](a)


if __name__ == "__main__":
    main()
