#!/bin/sh
set -o nounset
set -o errexit
set -x

echo "start version is $VER"

BUILD="${BUILD}"
VER="${VER}"

if [ "${VER}" != '${bamboo.jira.version}' ]; then
    TAR_DIR="peek_$VER"
else
    VER="b`date +%y%m%d.%H%M`"
    TAR_DIR="peek_$VER#$BUILD"
fi

DIR="deploy/$TAR_DIR"
mkdir -p $DIR

echo "New version is $VER"

# Source
mv rapui/src/rapui $DIR
mv peek/src/peek $DIR
mv $DIR/peek/PopupMenuItemMaker.py $DIR/peek/PopupMenuItemMaker.py_
#mv peek_server.doc/peekdoc $DIR

# Move the upgrade folder over
#mv peek_server/upgrade $DIR

# Prepare the packages
#BUILD_DIR=`pwd`
#cd $DIR/upgrade
#chmod +x *.sh
#
#./v1_pack.sh
#
#cd $BUILD_DIR

find $DIR -iname .git -exec rm -rf {} \; || true
find $DIR -iname "test" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "tests" -exec rm -rf {} \; 2> /dev/null || true
find $DIR -iname "*test.py" -exec rm -rf {} \; || true
find $DIR -iname "*tests.py" -exec rm -rf {} \; || true
find $DIR -iname ".Apple*" -exec rm -rf {} \; || true
find $DIR -iname "*TODO*" -exec rm -rf {} \; || true
find $DIR -iname ".idea" -exec rm -rf {} \; || true


# DB Upgrade
mv peek/alembic.ini $DIR
mv peek/alembic $DIR

# Init scripts, etc
mv peek/init/peek.init.deb.sh $DIR/peek.init.deb.sh
mv peek/init/peek.init.rhel.sh $DIR/peek.init.rhel.sh
mv peek/src/peek.py $DIR/peek.py

# Apply version number

for f in `grep -l -r  '#PEEK_VER#' .`; do
    echo "Updating version in file $f"
    sed -i "s/#PEEK_VER#/$VER/g" $f
done

for f in `grep -l -r  '#PEEK_BUILD#' .`; do
    echo "Updating build in file $f"
    sed -i "s/#PEEK_BUILD#/$BUILD/g" $f
done

echo "Compiling all python modules"
( cd $DIR && python -m compileall -f . )

echo "Deleting all source files"
find $DIR -name "*.py" -exec rm {} \;

mv $DIR/peek/PopupMenuItemMaker.py_ $DIR/peek/PopupMenuItemMaker.py

tar cjf ${TAR_DIR}.tar.bz2 -C deploy $TAR_DIR
