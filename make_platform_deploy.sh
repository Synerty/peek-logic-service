#!/bin/bash
set -o nounset
set -o errexit
set -x

echo "start version is $VER"

BUILD="${BUILD}"
VER="${VER}"

if [ "${VER}" == '${bamboo.jira.version}' ]; then
    VER="b`date +%y%m%d.%H%M`"
fi

echo "New version is $VER"
echo "New build is $BUILD"


cp -p peek_server/peek_platform_changelog.json deploy
cp -p peek_server/peek_platform_version.json deploy

PLAT_DIR="peek_platform_$VER#$BUILD"
mv deploy $PLAT_DIR

tar cjf ${PLAT_DIR}.tar.bz2 ${PLAT_DIR}
rm -rf ${PLAT_DIR}