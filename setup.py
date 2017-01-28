import os
import shutil
from distutils.core import setup

from setuptools import find_packages

package_name = "peek-server"
package_version = '0.0.10'

egg_info = "%s.egg-info" % package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

setup(
    name=package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    entry_points={
        'console_scripts': [
            'run_peek_server = peek_server.run_peek_server.main',
        ],
    },
    install_requires=["peek-platform", "peek-server-fe"],
    version=package_version,
    description='Peek Platform - Server Service',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
