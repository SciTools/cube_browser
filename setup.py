#!/usr/bin/env python

from __future__ import print_function

import os
from setuptools import setup


NAME = 'cube_browser'
DIR = os.path.abspath(os.path.dirname(__file__))


def extract_packages():
    packages = []
    root = os.path.join(DIR, 'lib', NAME)
    offset = len(os.path.dirname(root)) + 1
    for dpath, dnames, fnames in os.walk(root):
        if os.path.exists(os.path.join(dpath, '__init__.py')):
            package = dpath[offset:].replace(os.path.sep, '.')
            packages.append(package)
    return packages


def extract_version():
    version = None
    fname = os.path.join(DIR, 'lib', NAME, '__init__.py')
    with open(fname) as fin:
        for line in fin:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation.
                break
    return version


def extract_description():
    description = 'Cube Browser'
    fname = os.path.join(DIR, 'README.md')
    if os.path.isfile(fname):
        with open(fname) as fin:
            description = fin.read()
    return description


install_requires = ['iris']

setup_args = dict(
    name             = NAME,
    version          = extract_version(),
    description      = 'Cube Browser.',
    long_description = extract_description(),
    platforms        = ['Linux', 'Mac OS X', 'Windows'],
    license          = 'BSD 3-clause',
    url              = 'https://github.com/SciTools/cube_browser',
    package_dir      = {'': 'lib'},
    packages         = extract_packages(),
    classifiers      = [
        'License :: OSI Approved :: BSD License',
        'Development Status :: 1 - Planning Development Status',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries'],
    install_requires = install_requires,
    test_suite = '{}.tests'.format(NAME),
)


if __name__ == "__main__":
    setup(**setup_args)
