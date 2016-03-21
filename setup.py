#!/usr/bin/env python
# coding: utf-8


import os
import sys
from setuptools import setup, find_packages


setup(
    name='pymdc',
    description="Async and sync Metadisk API client for Python.",
    long_description=open("README.rst").read(),
    keywords="metadisk, api, client, python",
    url='http://storj.io',
    author='Matthew Roberts',
    author_email='matthew@storj.io',
    license="MIT",
    version="0.0.1",  # NOQA
    test_suite="tests",
    dependency_links=[],
    install_requires=open("requirements.txt").readlines()
)
