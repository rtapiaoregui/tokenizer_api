#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 09:53:43 2018

@author: rita
"""
import pytest
from custom_tokenizer import tokenizer

@pytest.fixture
def client():
    app = tokenizer.create_app()
    test_app = app.test_client()
    return test_app
