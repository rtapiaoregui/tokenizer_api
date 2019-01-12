#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 17:45:55 2018

@author: rita
"""
import json


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, 
                       data=json.dumps(json_dict), 
                       content_type='application/json')

def test_correct_submission (client):
    resp = post_json(client, '/tokenise/', {'input': 'This is an example.'})
    assert resp.status_code == 200

def test_bad_request_1 (client):
    resp = post_json(client, '/tokenise/', {'bad_json': 'This is an example.'})
    assert resp.status_code == 400
    
def test_bad_request_2 (client):
    resp = post_json(client, '/tokenise/', {'input': ''})
    assert resp.status_code == 400
    
def test_not_found_url (client):
    resp = post_json(client, '/wrong_url/', {'input': 'This is an example.'})
    assert resp.status_code == 404
