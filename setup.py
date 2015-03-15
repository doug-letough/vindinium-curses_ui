#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="vindinium-curses_ui",
    version="0.0.1",
    author="Sam Hocevar",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
)

