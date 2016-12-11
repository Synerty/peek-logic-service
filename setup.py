""" 
 * setup.py
 *
 *  Copyright Synerty Pty Ltd 2011
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'sqlalchemy',
    'alembic',
    'twisted',
    #'pycrypto', # required by twisted.conch
    #'pyasn1',   # required by twisted.conch
    'zope.interface',
    ]

setup(name='SynLACKY',
      version='0.1',
      description='Linux Command Lacky',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Jarrod Chesney',
      author_email='jarrod.chesney@synerty.com',
      url='',
      keywords='web shell linux twistd',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="SynLACKY",
#      entry_points = """\
#      [paste.app_factory]
#      main = SynLACKY:main
#      """,
#      paster_plugins=['pyramid'],
      )
