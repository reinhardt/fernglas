# -*- coding: utf-8 -*-
"""Installer for the fernglas package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.md') + \
    read('docs', 'CHANGELOG.md') + \
    read('docs', 'LICENSE.md')

setup(
    name='fernglas',
    version='0.1',
    description="Checks deployment status of a commit",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
    ],
    keywords='git,deployment,buildout',
    author='Manuel Reinhardt',
    author_email='reinhardt@syslab.com',
    url='http://pypi.python.org/pypi/fernglas',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=[],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'GitPython',
        'paramiko',
    ],
    extras_require={
    },
    entry_points="""
        [console_scripts]
        fernglas = fernglas:main
    """,
)
