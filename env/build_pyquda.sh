#!/bin/bash
# Build PyQUDA (pinned) against /opt/quda.
set -euo pipefail
export QUDA_PATH=/opt/quda
PYQUDA_VERSION=${PYQUDA_VERSION:-0.10.54}
python3 -m pip install --no-cache-dir --no-build-isolation "pyquda==${PYQUDA_VERSION}" "pyquda-utils==${PYQUDA_VERSION}.post0"
