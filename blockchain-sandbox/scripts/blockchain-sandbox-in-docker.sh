#!/bin/bash

# requirements:
# docker_image points to a docker image with taurus-node built
# with flag EOSIO_NOT_REQUIRE_FULL_VALIDATION=on when doing cmake

set -e

mydir=$(dirname $(readlink -f $0))
repo_root=$(readlink -f ${mydir}/..)

docker_image=$1
snapshot=$2

if [[ "$docker_image" == "" ]]; then
  echo "Usage: $0 docker_image_path [snapshot path]"
  exit 3
fi

snapshot_arg=""
docker_snapshot_bind_arg=""
info_msg=""

if [[ "$snapshot" != "" ]]; then
  snapshot_arg="--snapshot /blockchain-snapshot.bin"
  docker_snapshot_bind_arg="-v $(readlink -f ${snapshot}):/blockchain-snapshot.bin"
  info_msg=" with snapshot ${snapshot}"
fi

echo "Pull docker images for taurus-node debug version ${docker_image}"
docker pull ${docker_image}

echo "Start blockchain sandbox${info_msg} ..."

docker run \
  --rm -ti --name blockchain-sandbox \
  -v ${repo_root}:/blockchain-sandbox ${docker_snapshot_bind_arg} \
  -p 127.0.0.1:8888:8888 -p 127.0.0.1:8880:8880 -p 127.0.0.1:5672:5672 -p 127.0.0.1:15672:15672 \
  ${docker_image} /blockchain-sandbox/scripts/blockchain-sandbox.sh ${snapshot_arg}
