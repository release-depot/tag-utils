#!/usr/bin/env python

import json

import requests


from .common import tidy_nevra


def fetch_json_data(url):
    ret = requests.get(url)
    if ret.status_code == 200:
        return json.loads(ret.text)


def json_api_as_nevr(url):
    md = fetch_json_data(url)
    ret = {}
    for p in md['packages']:
        ret[p['name']] = tidy_nevra(p['nvr'])
    return ret
