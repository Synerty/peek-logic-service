#!/bin/sh
set -o nounset
set -o errexit
set -x

echo "start version is $VER"

BUILD="${BUILD}"
VER="${VER}"
DATE="`date --utc`"

if [ "${VER}" == '${bamboo.jira.version}' ]; then
    VER="b`date +%y%m%d.%H%M`"
fi

echo "New version is $VER"
echo "New build is $BUILD"

TAR_DIR="peek_server_$VER#$BUILD"
DIR="deploy/$TAR_DIR"
mkdir -p $DIR


# Source
cp -pr rapui/src/rapui $DIR
cp -pr peek_server/src/peek_server $DIR

find $DIR -iname .git -exec rm -rf {} \; || true
find $DIR -iname "test" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "tests" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "*test.py" -exec rm -rf {} \; || true
find $DIR -iname "*tests.py" -exec rm -rf {} \; || true
find $DIR -iname ".Apple*" -exec rm -rf {} \; || true
find $DIR -iname "*TODO*" -exec rm -rf {} \; || true
find $DIR -iname ".idea" -exec rm -rf {} \; || true


# DB Upgrade
ln -s /home/peek/peek.home/config.cfg $DIR/alembic.ini
cp -pr peek_server/alembic $DIR

# Init scripts, etc
cp -pr peek_server/init/peek_server.init.deb.sh $DIR/peek_server.init.deb.sh
cp -pr peek_server/init/peek_server.init.rhel.sh $DIR/peek_server.init.rhel.sh
cp -p peek_server/src/run_peek_server.py $DIR/

# Apply version number

for f in `grep -l -r  '#PEEK_VER#' .`; do
    echo "Updating version in file $f"
    sed -i "s/#PEEK_VER#/$VER/g" $f
done

for f in `grep -l -r  '#PEEK_BUILD#' .`; do
    echo "Updating build in file $f"
    sed -i "s/#PEEK_BUILD#/$BUILD/g" $f
done

for f in `grep -l -r  '#BUILD_DATE#' .`; do
    echo "Updating date in file $f"
    sed -i "s/#BUILD_DATE#/$DATE/g" $f
done

echo "Compiling all python modules"
( cd $DIR && python -m compileall -f . )

echo "Deleting all source files"
find $DIR -name "*.py" -exec rm {} \;

pushd deploy
tar cjf ${TAR_DIR}.tar.bz2 -C deploy $TAR_DIR

rm -rf $TAR_DIR
popd
