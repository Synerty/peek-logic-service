import os
import shutil

from setuptools import find_packages
from setuptools import setup

###############################################################################
# Define variables
#
# Modify these values to fork a new plugin
#

author = "Synerty"
author_email = "contact@synerty.com"
py_package_name = "peek_logic_service"
pip_package_name = py_package_name.replace("_", "-")
package_version = "0.0.0"
description = "Peek Logic Service."

download_url = "https://bitbucket.org/synerty/%s/get/%s.zip"
download_url %= pip_package_name, package_version
url = "https://bitbucket.org/synerty/%s" % pip_package_name

###############################################################################
# Customise the package file finder code

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

excludePathContains = ("__pycache__", "node_modules", "platforms", "dist")
excludeFilesEndWith = (".pyc", ".js", ".js.map", ".lastHash")
excludeFilesStartWith = ()


def find_package_files():
    paths = []
    for (path, directories, filenames) in os.walk(py_package_name):
        if [e for e in excludePathContains if e in path]:
            continue

        for filename in filenames:
            if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                continue

            if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                continue

            paths.append(os.path.join(path[len(py_package_name) + 1 :], filename))

    return paths


package_files = find_package_files()

###############################################################################
# Define the dependencies

# Ensure the dependency is the same major number
# and no older then this version

requirements = ["peek-plugin-base", "peek-platform", "peek-admin-app", "peek-admin-doc"]

# Force the dependencies to be the same branch
reqVer = ".".join(package_version.split(".")[0:2]) + ".*"

# >=2.0.*,>=2.0.6
requirements = [
    "%s==%s,>=%s" % (pkg, reqVer, package_version) if pkg.startswith("peek") else pkg
    for pkg in requirements
]

###############################################################################
# Call the setuptools

setup(
    entry_points={
        "console_scripts": [
            "run_peek_logic_service = peek_logic_service.run_peek_logic_service:main",
            "run_peek_logic_service_build_only = peek_logic_service.run_peek_logic_service_build_only:main",
            "winsvc_peek_logic_service = peek_logic_service.winsvc_peek_logic_service:main",
        ],
    },
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"": package_files},
    install_requires=requirements,
    zip_safe=False,
    version=package_version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    keywords=["Peek", "Python", "Platform", "synerty"],
    classifiers=[],
)
