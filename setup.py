#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 10:44:37 2018

@author: rita
"""

import os
from setuptools import setup

setup(
    name = "tokenizer_api",
    version = "0.1",
    author = "Rita Tapia Oregui",
    author_email = "rtapiaoregui@gmail.com",
    description = ("RESTful API for tokenization with Spacy"),
    keywords = "Test case for hiring process",
    url = "http://github.com/rtapiaoregui/tokenizer_api",
    packages=['custom_tokenizer'],
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    install_requires=['spacy', 'flask', 'pyenchant', 'flask_restful'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-flask'],
    include_package_data=True,
    )
