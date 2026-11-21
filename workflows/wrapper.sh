#!/bin/bash
# Job entrypoint inside the rhadron Apptainer image.  Usage: wrapper.sh <rhadron cli args...>
# The code tarball (code.tar.gz, made by workflows/manifest.py at a committed git SHA) is unpacked
# into the job sandbox; outputs go to ./out (transferred back ON_EXIT_OR_EVICT).
set -euo pipefail
echo "host: $(hostname)  start: $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo "no GPU"
mkdir -p code out
tar -xzf code.tar.gz -C code
export PYTHONPATH="$PWD/code:${PYTHONPATH:-}"
export RHADRON_GIT_SHA="$(cat code/GIT_SHA)"
export CUPY_CACHE_DIR="$PWD/.cupy"
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
export QUDA_RESOURCE_PATH="$PWD/out/quda_tune"; mkdir -p "$QUDA_RESOURCE_PATH"
python3 -u -m rhadron.cli "$@"
rc=$?
echo "end: $(date -u +%FT%TZ) rc=$rc"
exit $rc
