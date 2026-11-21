#!/bin/bash
# Build QUDA (develop at a pinned SHA) for Wilson/clover with multigrid, single-node MPI.
set -euo pipefail
QUDA_SHA=${QUDA_SHA:-af7e15080e247795ef076b6d9284478755a9a683}
ARCHS=${ARCHS:-"70-real;75-real;80-real;86-real;89-real;90-real;90-virtual"}
JOBS=${JOBS:-48}
mkdir -p /opt/build && cd /opt/build
git clone https://github.com/lattice/quda.git quda-src
cd quda-src && git checkout "$QUDA_SHA"
# QUDA sets a single CUDA architecture; allow a list (fat binary) for the heterogeneous OSPool.
# Feature level (QUDA_COMPUTE_CAPABILITY) stays at the minimum, sm_70.
sed -i 's|^set_target_properties(quda PROPERTIES CUDA_ARCHITECTURES ${CMAKE_CUDA_ARCHITECTURES})|if(DEFINED ENV{QUDA_FAT_ARCHS})\n  set(CMAKE_CUDA_ARCHITECTURES "$ENV{QUDA_FAT_ARCHS}")\nendif()\nset_target_properties(quda PROPERTIES CUDA_ARCHITECTURES "${CMAKE_CUDA_ARCHITECTURES}")|' \
    lib/targets/cuda/target_cuda.cmake
grep -n QUDA_FAT_ARCHS lib/targets/cuda/target_cuda.cmake
export QUDA_FAT_ARCHS="$ARCHS"
mkdir -p build && cd build
cmake .. -G Ninja -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/opt/quda \
    -DQUDA_GPU_ARCH=sm_70 \
    -DQUDA_DIRAC_DEFAULT_OFF=ON -DQUDA_DIRAC_WILSON=ON -DQUDA_DIRAC_CLOVER=ON -DQUDA_DIRAC_LAPLACE=ON \
    -DQUDA_DIRAC_COVDEV=ON \
    -DQUDA_MULTIGRID=ON -DQUDA_MULTIGRID_NVEC_LIST="24,32" \
    -DQUDA_MPI=ON -DQUDA_INTERFACE_MILC=OFF -DQUDA_INTERFACE_QDP=ON \
    -DQUDA_BUILD_ALL_TESTS=OFF -DQUDA_INSTALL_ALL_TESTS=OFF -DQUDA_DOWNLOAD_EIGEN=ON
ninja -j "$JOBS"
ninja install
cd /opt/build && rm -rf quda-src/build
