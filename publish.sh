#!/usr/bin/env bash

set -o nounset
set -o errexit

#------------------------------------------------------------------------------
# Prechecks



if [ -n "$(git status --porcelain)" ]; then
    echo "There are uncommitted changes, please make sure all changes are committed" >&2
    exit 1
fi

VER="${1:?You must pass a version of the format 0.0.0 as the only argument}"

DEVBUILD=0
if echo ${VER} | grep -q '[[:alpha:]]'; then
    echo "This is a DEV build"
    DEVBUILD=1
fi

if git tag | grep -q "^${VER}$"; then
    echo "Git tag for version ${VER} already exists." >&2
    exit 1
fi

#------------------------------------------------------------------------------
# Configure package preferences here

source ./publish.settings.sh

PIP_PACKAGE=${PY_PACKAGE//_/-} # Replace _ with -

HAS_GIT=$(ls -d .git 2>/dev/null)

#------------------------------------------------------------------------------
# Set the versions
echo "Setting version to $VER"

VER_FILES="${VER_FILES}"
VER_FILES="${VER_FILES} ${PY_PACKAGE}/__init__.py"
VER_FILES="${VER_FILES} ${PY_PACKAGE}/plugin_package.json"

function updateFileVers() {
    for file in ${VER_FILES}
    do
        if [ -f ${file} ]
        then
            sed -i "s/^__version__.*/__version__ = \'${VER}\'/g" ${file}
            sed -i "s/0.0.0/${VER}/g" ${file}
        fi
    done

    # update version in pyproject.toml
    sed -i 's/version = "0.0.0"/version = "'${VER}'"/g' pyproject.toml
    # update peek dependencies version in pyproject.toml
    # e.g.
    # replace "peek-admin-doc==0.0.*,>=0.0.0" with
    #   "peek-admin-doc==4.1.*,>=4.1.2+b12345"
    #   given version 4.1.0+b12345
    _versionArray=( ${VER//./ } )
    VERSION_MAJOR="${_versionArray[0]}"
    VERSION_MINOR="${_versionArray[1]}"
    sed 's/\(peek-.*==\).*\(,>=\)0.0.0/\1'"${VERSION_MAJOR}"'.'"${VERSION_MINOR}"'.\*\2'"${VER}"'/g' pyproject.toml

}

# Apply the version to the other files
updateFileVers

#------------------------------------------------------------------------------
# Clear out old files

rm -rf build dist *.egg-info

#------------------------------------------------------------------------------
# Create the package and upload to pypi

python -m build --sdist

if [ ${PYPI_PUBLISH} == "1" -a ${DEVBUILD} -eq 0 ]; then
    echo "Publishing ${PIP_PACKAGE} to PyPI"
    twine upload dist/${PIP_PACKAGE}-${VER}.tar.gz
fi

#------------------------------------------------------------------------------
# Reset the commit, we don't want versions in the commit
# Tag and push this release
if [ $HAS_GIT ]; then
    # We need to commit the config file with the version for Read The Docs
    if [ -n "${VER_FILES_TO_COMMIT}" -a ${DEVBUILD} -eq 0 ]; then
        git add ${VER_FILES_TO_COMMIT}
        git commit -m "Updated conf.py to ${VER}"
    fi

    git reset --hard

    if [ ${DEVBUILD} -eq 0 ]; then
        echo "Tagging ${PIP_PACKAGE}"
        git tag ${VER}

        echo "Pushing ${PIP_PACKAGE} to BitBucket"
        git push
        git push --tags
    fi

fi

#------------------------------------------------------------------------------
# All done

echo "Publish Complete"
