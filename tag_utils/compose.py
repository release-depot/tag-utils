#!/usr/bin/python3

from toolchest.rpm.utils import drop_epoch

import requests
import os
import json

def fetch_rpm_metadata(baseurl, compose_id):
    full_url = os.path.join(baseurl, compose_id, 'compose/metadata/rpms.json')
    ret = requests.get(full_url)
    if ret.status_code == 200:
        return json.loads(ret.text)


def compose_builds(rpm_metadata):
    try:
        compose_id = rpm_metadata['payload']['compose']['id']
    except KeyError:
        raise Exception('Could not parse compose metadata')

    ret_builds = set()
    rpminfo = rpm_metadata['payload']['rpms']
    for variant in rpminfo:
        for arch in rpminfo[variant]:
            for srpm in rpminfo[variant][arch]:
                if srpm.endswith('.src'):
                    srpm = srpm[:-4]
                srpm = drop_epoch(srpm)
                ret_builds = ret_builds | set([srpm])

    return sorted(list(ret_builds))


