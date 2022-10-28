#!/usr/bin/env bash
. /opt/rh/devtoolset-11/enable
set -euo pipefail -x

gcc_version=12.2.0
echo "GCC version: ${gcc_version}"
src_tag=releases/gcc-${gcc_version}
gcc_git_url=https://github.com/gcc-mirror/gcc

timestamp=$( date +%Y-%m-%dT%H_%M_%S )
tag=v${gcc_version}-${timestamp}-centos7-$( uname -m )
dir_name=yb-gcc-${tag}
mkdir -p /opt/yb-build/gcc
gcc_prefix_dir=/opt/yb-build/gcc/${dir_name}
build_parent_dir=${gcc_prefix_dir}-build
build_dir=${build_parent_dir}/build
rm -rf "${build_parent_dir}"
src_dir="${build_parent_dir}/src"
git clone --branch "${src_tag}" "${gcc_git_url}" "${src_dir}"
mkdir -p "${build_dir}"
cd "${build_dir}"

mkdir -p "${HOME}/logs"
log_path=$HOME/logs/build_gcc_${dir_name}.log
echo "Logging to ${log_path}"
time (
  "${src_dir}/configure" "--prefix=${gcc_prefix_dir}" --enable-languages=c,c++ --disable-multilib
  make -j80
  make install
) 2>&1 | tee "${log_path}"
echo "Log saved to ${log_path}"

cd /opt/yb-build/gcc
archive_name=${dir_name}.tar.gz
tar czf "${archive_name}" "${dir_name}"
sha256sum "${archive_name}" >"${archive_name}.sha256"
hub release create "${tag}" -a "${archive_name}" "${archive_name}.sha256"
