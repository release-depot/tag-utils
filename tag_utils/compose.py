#!/usr/bin/env python

import requests
import os
import json

from toolchest.rpm.utils import componentize

from .common import tidy_nevra


def check_compose(url):
    full_url = os.path.join(url, 'STATUS')
    ret = requests.get(full_url)
    if ret.status_code == 200:
        if ret.text.startswith('FINISHED'):
            return True
        raise ValueError('Compose status invalid: ' + ret.text)
    raise ValueError('Failed to check compose; HTTP code ' + str(ret.status_code))


def fetch_rpm_metadata(url):
    check_compose(url)
    full_url = os.path.join(url, 'compose/metadata/rpms.json')
    ret = requests.get(full_url)
    if ret.status_code == 200:
        return json.loads(ret.text)


def compose_builds(rpm_metadata):
    try:
        compose_id = rpm_metadata['payload']['compose']['id']  # NOQA
    except KeyError:
        raise Exception('Could not parse compose metadata')

    ret_builds = set()
    rpminfo = rpm_metadata['payload']['rpms']
    for variant in rpminfo:
        for arch in rpminfo[variant]:
            for srpm in rpminfo[variant][arch]:
                if srpm.endswith('.src'):
                    srpm = srpm[:-4]
                ret_builds = ret_builds | set([srpm])

    return sorted(list(ret_builds))


def compose_as_nevr(url):
    check_compose(url)
    md = fetch_rpm_metadata(url)
    builds = compose_builds(md)
    ret = {}
    for build in builds:
        ret[componentize(build)] = tidy_nevra(build)
    return ret
