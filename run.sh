#!/usr/bin/env bash

IMAGE='lapp-dvde004:5000/deploy-tool:2.0'
BACKUP_PATH=$($PWD/backups/)

# fs: backups/, <jsons>/

mkdir -p ${BACKUP_PATH}

#docker pull ${IMAGE}
docker run -ti --rm --net host -v ${BACKUP_PATH}:/deploytool/backups/ ${IMAGE} $@
