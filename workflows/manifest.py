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


def glue_dag(a):
    """Re-measurement DAG: every stored configuration whose *_glue.h5 is missing or was produced by
    code older than --good-since (git ancestry), batched per stream."""
    ens = yaml.safe_load(open(a.ensemble))
    tag = ens["tag"]
    base = os.path.join(DATA, tag)
    dagdir = os.path.join(base, "glue_dag")
    os.makedirs(os.path.join(dagdir, "logs"), exist_ok=True)
    sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
    shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
    shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)

    def good(path):
        try:
            with h5py.File(path, "r") as f:
                s = str(f.attrs.get("git_sha", ""))
        except Exception:  # noqa: BLE001
            return False
        r = subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", a.good_since, s],
                           capture_output=True)
        return r.returncode == 0

    import glob as _glob
    todo = {}
    for cfgp in sorted(_glob.glob(os.path.join(base, "s*", "out", f"{tag}_s*_c[0-9][0-9][0-9][0-9].h5"))):
        gp = cfgp.replace(".h5", "_glue.h5")
        if not (os.path.exists(gp) and good(gp)):
            todo.setdefault(os.path.dirname(os.path.dirname(cfgp)), []).append(cfgp)
    lines = [f"# {tag} gluelump re-measurement; code {sha}", f"CONFIG {dagdir}/dagman.config"]
    n = 0
    for sdir, cfgs in todo.items():
        for k in range(0, len(cfgs), a.batch):
            chunk = cfgs[k:k + a.batch]
            node = f"glue_{os.path.basename(sdir)}_{k // a.batch}"
            inputs = ",".join([os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml")] + chunk)
            args = "glue --ensemble ens.yaml --outdir out --configs " + " ".join(os.path.basename(c) for c in chunk)
            lines.append(f"JOB {node} {dagdir}/glue.sub")
            lines.append(f'VARS {node} IWD="{sdir}" INPUTS="{inputs}" ARGS="{args}" NODE="{node}"')
            lines.append(f"RETRY {node} 3")
            n += len(chunk)
    sub = f"""universe = vanilla
container_image = {a.image}
executable = {dagdir}/wrapper.sh
arguments = $(ARGS)
initialdir = $(IWD)
should_transfer_files = YES
transfer_input_files = $(INPUTS)
transfer_output_files = out
when_to_transfer_output = ON_EXIT_OR_EVICT
request_gpus = 1
require_gpus = {a.gpureq}
request_cpus = 1
request_memory = {a.mem}
request_disk = {a.disk}
log = {dagdir}/logs/glue.log
output = {dagdir}/logs/$(NODE).out
error = {dagdir}/logs/$(NODE).err
queue
"""
    open(os.path.join(dagdir, "glue.sub"), "w").write(sub)
    open(os.path.join(dagdir, "dagman.config"), "w").write(
        f"DAGMAN_MAX_JOBS_SUBMITTED = {a.maxjobs}\nDAGMAN_MAX_JOBS_IDLE = {a.maxjobs}\n")
    dag = os.path.join(dagdir, f"{tag}_glue.dag")
    open(dag, "w").write("\n".join(lines) + "\n")
    print(dag, f"{n} configurations")


def quark_dag(a):
    """Quark production DAG: per stored configuration, one resumable `solve` node per kappa role
    (GPU, QUDA image) and a `contract` node (GPU, CuPy) depending on all of them.  Configurations
    whose *_quark.h5 exists are skipped; partial propagator files are fed back via --resume."""
    import glob as _glob

    ens = yaml.safe_load(open(a.ensemble))
    tag = ens["tag"]
    base = os.path.join(DATA, tag)
    dagdir = os.path.join(base, "quark_dag")
    qdir = os.path.join(base, "quark")
    os.makedirs(os.path.join(dagdir, "logs"), exist_ok=True)
    os.makedirs(qdir, exist_ok=True)
    sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
    shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
    shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)
    roles = list(ens["quark"]["kappas"])
    if a.nucleon_roles:
        dagdir = os.path.join(base, "nucleon_dag")
        os.makedirs(os.path.join(dagdir, "logs"), exist_ok=True)
        sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
        shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
        shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)
    if a.pwave_role:
        dagdir = os.path.join(base, "pwave_dag")
        os.makedirs(os.path.join(dagdir, "logs"), exist_ok=True)
        sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
        shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
        shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)
    cfgs = sorted(_glob.glob(os.path.join(base, "s*", "out", f"{tag}_s*_c[0-9][0-9][0-9][0-9].h5")))
    if a.every > 1:
        cfgs = [c for c in cfgs if int(c[-7:-3]) % a.every == 0]
    if a.limit:
        cfgs = cfgs[: a.limit]
    lines = [f"# {tag} quark production; code {sha}; roles {roles}", f"CONFIG {dagdir}/dagman.config"]
    n = 0
    for c in cfgs:
        name = os.path.basename(c)[:-3]
        if a.contract_only:
            props = [os.path.join(qdir, "out", f"{name}_prop_{r}.h5") for r in roles]
            if not all(os.path.exists(p) for p in props) or os.path.exists(os.path.join(qdir, "out", name + "_quark.h5")):
                continue
            cnode = f"c_{name}"
            lines.append(f"JOB {cnode} {dagdir}/contract.sub")
            lines.append(f'VARS {cnode} NODE="{cnode}" INPUTS="{",".join([os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml"), c] + props)}" '
                         f'ARGS="contract --ensemble ens.yaml --config {os.path.basename(c)} --props {" ".join(os.path.basename(p) for p in props)} --outdir out"')
            lines.append(f"RETRY {cnode} 3")
            n += 1
            continue
        if a.nucleon_roles:
            if not os.path.exists(os.path.join(qdir, "out", name + "_quark.h5")):
                continue  # same configuration set as the M3 quark data
            for r in a.nucleon_roles.split(","):
                nf = os.path.join(qdir, "out", f"{name}_nuc_{r}.h5")
                node = f"n_{name}_{r}"
                inputs = [os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml"), c]
                resume = ""
                if os.path.exists(nf):
                    inputs.append(nf)
                    resume = f"--resume {os.path.basename(nf)}"
                lines.append(f"JOB {node} {dagdir}/solve.sub")
                lines.append(f'VARS {node} NODE="{node}" INPUTS="{",".join(inputs)}" '
                             f'ARGS="solve --nucleon --ensemble ens.yaml --config {os.path.basename(c)} --role {r} {resume} --outdir out"')
                lines.append(f"RETRY {node} 3")
            n += 1
            continue
        if a.pwave_role:
            pw = os.path.join(qdir, "out", f"{name}_pw_{a.pwave_role}.h5")
            node = f"p_{name}"
            inputs = [os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml"), c]
            resume = ""
            if os.path.exists(pw):
                inputs.append(pw)
                resume = f"--resume {os.path.basename(pw)}"
            lines.append(f"JOB {node} {dagdir}/solve.sub")
            lines.append(f'VARS {node} NODE="{node}" INPUTS="{",".join(inputs)}" '
                         f'ARGS="solve --pwave --ensemble ens.yaml --config {os.path.basename(c)} --role {a.pwave_role} {resume} --outdir out"')
            lines.append(f"RETRY {node} 3")
            n += 1
            continue
        if os.path.exists(os.path.join(qdir, "out", name + "_quark.h5")):
            continue
        props = []
        for r in roles:
            node = f"s_{name}_{r}"
            prop = os.path.join(qdir, "out", f"{name}_prop_{r}.h5")
            props.append(prop)
            inputs = [os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml"), c]
            resume = ""
            if os.path.exists(prop):
                inputs.append(prop)
                resume = f"--resume {os.path.basename(prop)}"
            lines.append(f"JOB {node} {dagdir}/solve.sub")
            lines.append(f'VARS {node} NODE="{node}" INPUTS="{",".join(inputs)}" '
                         f'ARGS="solve --ensemble ens.yaml --config {os.path.basename(c)} --role {r} {resume} --outdir out"')
            lines.append(f"RETRY {node} 3")
        cnode = f"c_{name}"
        lines.append(f"JOB {cnode} {dagdir}/contract.sub")
        lines.append(f'VARS {cnode} NODE="{cnode}" INPUTS="{",".join([os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml"), c] + props)}" '
                     f'ARGS="contract --ensemble ens.yaml --config {os.path.basename(c)} --props {" ".join(os.path.basename(p) for p in props)} --outdir out"')
        lines.append(f"RETRY {cnode} 3")
        lines.append(f"PRIORITY {cnode} 100")  # contract as soon as a config's solves are done
        for r in roles:
            lines.append(f"PRIORITY s_{name}_{r} {max(0, 50 - n // 4)}")  # finish configs in order
        lines.append(f"PARENT {' '.join(f's_{name}_{r}' for r in roles)} CHILD {cnode}")
        n += 1
    common = f"""universe = vanilla
executable = {dagdir}/wrapper.sh
arguments = $(ARGS)
initialdir = {qdir}
should_transfer_files = YES
transfer_input_files = $(INPUTS)
transfer_output_files = out
when_to_transfer_output = ON_EXIT_OR_EVICT
request_gpus = 1
request_cpus = 1
periodic_release = (HoldReasonCode == 13 || HoldReasonCode == 12) && (NumJobStarts < 6)
log = {dagdir}/logs/quark.log
output = {dagdir}/logs/$(NODE).out
error = {dagdir}/logs/$(NODE).err
"""
    open(os.path.join(dagdir, "solve.sub"), "w").write(
        common + f"container_image = {a.image_quda}\nrequire_gpus = {a.gpureq}\nrequest_memory = {a.mem}\n"
                 f"request_disk = {a.disk}\nqueue\n")
    open(os.path.join(dagdir, "contract.sub"), "w").write(
        common + f"container_image = {a.image_gen}\nrequire_gpus = (Capability >= 6.0) && (GlobalMemoryMb >= 7000)\n"
                 f"request_memory = {a.mem}\nrequest_disk = {a.disk}\nqueue\n")
    open(os.path.join(dagdir, "dagman.config"), "w").write(
        f"DAGMAN_MAX_JOBS_SUBMITTED = {a.maxjobs}\nDAGMAN_MAX_JOBS_IDLE = {a.maxjobs}\n")
    dag = os.path.join(dagdir, f"{tag}_{'nucleon' if a.nucleon_roles else ('pwave' if a.pwave_role else 'quark')}.dag")
    open(dag, "w").write("\n".join(lines) + "\n")
    print(dag, f"{n} configurations x {len(roles)} roles")


def hmc_dag(a):
    """Stage B: linear chains of HMC segments per stream (`rhadron hmc --until <traj>`), resuming from
    the checkpoint; segments whose checkpoint already shows the target trajectory are DONE."""
    ens = yaml.safe_load(open(a.ensemble))
    tag = ens["tag"]
    base = os.path.join(DATA, tag)
    dagdir = os.path.join(base, "dag")
    os.makedirs(dagdir, exist_ok=True)
    sha = code_tarball(os.path.join(dagdir, "code.tar.gz"))
    shutil.copy(a.ensemble, os.path.join(dagdir, "ens.yaml"))
    shutil.copy(os.path.join(HERE, "wrapper.sh"), dagdir)
    h = ens["hmc"]
    total = int(h["n_therm"]) + int(h["save_every"]) * a.cfgs_per_stream
    lines = [f"# {tag}: {a.streams} streams x {a.cfgs_per_stream} cfgs (HMC); code {sha}", f"CONFIG {dagdir}/dagman.config"]
    for s_ in range(a.streams):
        iwd = os.path.join(base, f"s{s_}")
        os.makedirs(os.path.join(iwd, "logs"), exist_ok=True)
        ck = os.path.join(iwd, "out", f"{tag}_s{s_}_ckpt.h5")
        try:
            with h5py.File(ck, "r") as f:
                have = int(f.attrs["traj"])
        except Exception:  # noqa: BLE001
            have = -1
        prev = None
        for k, u in enumerate(list(range(a.segment, total, a.segment)) + [total]):
            node = f"h_s{s_}_{k}"
            inputs = [os.path.join(dagdir, "code.tar.gz"), os.path.join(dagdir, "ens.yaml")]
            startarg = ""
            if k > 0 or have > 0:
                inputs.append(ck)
                startarg = f"--start {os.path.basename(ck)}"
            lines.append(f"JOB {node} {dagdir}/hmc.sub" + (" DONE" if have >= u else ""))
            lines.append(f'VARS {node} STREAM="{s_}" UNTIL="{u}" IWD="{iwd}" INPUTS="{",".join(inputs)}" STARTARG="{startarg}"')
            lines.append(f"RETRY {node} 3")
            if prev:
                lines.append(f"PARENT {prev} CHILD {node}")
            prev = node
    sub = f"""universe = vanilla
container_image = {a.image}
executable = {dagdir}/wrapper.sh
arguments = hmc --ensemble ens.yaml --stream $(STREAM) --until $(UNTIL) $(STARTARG) --outdir out
initialdir = $(IWD)
should_transfer_files = YES
transfer_input_files = $(INPUTS)
transfer_output_files = out
when_to_transfer_output = ON_EXIT_OR_EVICT
request_gpus = 1
require_gpus = {a.gpureq}
request_cpus = 1
request_memory = 8GB
request_disk = 10GB
priority = 10
periodic_release = (HoldReasonCode == 13 || HoldReasonCode == 12) && (NumJobStarts < 6)
log = $(IWD)/logs/{tag}_s$(STREAM).log
output = $(IWD)/logs/{tag}_s$(STREAM)_u$(UNTIL).out
error = $(IWD)/logs/{tag}_s$(STREAM)_u$(UNTIL).err
queue
"""
    open(os.path.join(dagdir, "hmc.sub"), "w").write(sub)
    open(os.path.join(dagdir, "dagman.config"), "w").write(
        f"DAGMAN_MAX_JOBS_SUBMITTED = {a.maxjobs}\nDAGMAN_MAX_JOBS_IDLE = {a.maxjobs}\n")
    dag = os.path.join(dagdir, f"{tag}_hmc.dag")
    open(dag, "w").write("\n".join(lines) + "\n")
    print(dag, f"{a.streams} streams, {total} trajectories each")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("ensemble")
    g.add_argument("--streams", type=int, required=True)
    g.add_argument("--segment", type=int, required=True, help="compound sweeps per job")
    g.add_argument("--image", required=True)
    # FP64-capable GPUs only (V100/A100/H100): the CuPy heatbath is complex128; consumer/A40-class
    # cards run FP64 at 1/32-1/64 rate and were measured 3-5x slower overall.
    g.add_argument("--gpureq", default="(Capability == 7.0 || Capability == 8.0 || Capability == 9.0) && (GlobalMemoryMb >= 7000)")
    g.add_argument("--mem", default="8GB")
    g.add_argument("--disk", default="8GB")
    g.add_argument("--maxjobs", type=int, default=40)
    gd = sub.add_parser("glue")
    gd.add_argument("ensemble")
    gd.add_argument("--good-since", required=True, help="first git SHA with the deterministic basis")
    gd.add_argument("--batch", type=int, default=20)
    gd.add_argument("--image", required=True)
    gd.add_argument("--gpureq", default="(Capability == 7.0 || Capability == 8.0 || Capability == 9.0) && (GlobalMemoryMb >= 7000)")
    gd.add_argument("--mem", default="8GB")
    gd.add_argument("--disk", default="10GB")
    gd.add_argument("--maxjobs", type=int, default=10)
    qd = sub.add_parser("quark")
    qd.add_argument("ensemble")
    qd.add_argument("--image-quda", required=True)
    qd.add_argument("--image-gen", required=True)
    qd.add_argument("--gpureq", default="(Capability >= 7.0) && (GlobalMemoryMb >= 20000) && (Capability < 10.0)")  # no sm_120 kernels in the CUDA 12.4 image
    qd.add_argument("--mem", default="8GB")
    qd.add_argument("--disk", default="12GB")
    qd.add_argument("--maxjobs", type=int, default=20)
    qd.add_argument("--every", type=int, default=1, help="use every n-th configuration")
    qd.add_argument("--limit", type=int, default=0)
    qd.add_argument("--pwave-role", default=None, help="static-light P-wave DAG for this kappa role only")
    qd.add_argument("--contract-only", action="store_true", help="contraction nodes only (from existing prop files)")
    qd.add_argument("--nucleon-roles", default=None, help="smeared-sink nucleon DAG for these roles (comma list)")
    hd = sub.add_parser("hmc")
    hd.add_argument("ensemble")
    hd.add_argument("--streams", type=int, default=4)
    hd.add_argument("--cfgs-per-stream", type=int, default=100)
    hd.add_argument("--segment", type=int, default=40, help="trajectories per job")
    hd.add_argument("--image", required=True)
    hd.add_argument("--gpureq", default="(Capability == 7.0 || Capability == 8.0 || Capability == 9.0) && (GlobalMemoryMb >= 15000)")
    hd.add_argument("--maxjobs", type=int, default=8)
    r = sub.add_parser("refresh-code")
    r.add_argument("tag")
    a = p.parse_args()
    {"gen": gen_dag, "glue": glue_dag, "quark": quark_dag, "hmc": hmc_dag, "refresh-code": refresh_code}[a.cmd](a)


if __name__ == "__main__":
    main()
