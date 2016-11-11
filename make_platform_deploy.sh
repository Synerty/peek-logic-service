#!/bin/bash
set -o nounset
set -o errexit
set -x

function convertBambooDate() {
# EG s="2010-01-01T01:00:00.000+01:00"
# TO 100101.0100
python <<EOF
from dateutil.parser import parse
print parse("${BAMBOO_DATE}").strftime('%y%m%d.%H%M')
EOF
}
echo "start version is $VER"

BUILD="${BUILD}"
VER="${VER}"
DATE="`convertBambooDate`"

if [ "${VER}" == '${bamboo.jira.version}' ]; then
    VER="b${DATE}"
fi

echo "New version is $VER"
echo "New build is $BUILD"


cp -p peek_server/peek_platform_changelog.json deploy
cp -p peek_server/peek_platform_version.json deploy

PLAT_DIR="peek_platform_$VER#$BUILD"
mv deploy $PLAT_DIR

tar cjf ${PLAT_DIR}.tar.bz2 ${PLAT_DIR}
rm -rf ${PLAT_DIR}