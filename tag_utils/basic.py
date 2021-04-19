#!/usr/bin/env python

import sys

from toolchest.rpm.utils import componentize
from toolchest.strutil import list_or_splitstr, split_file

from .common import tidy_nevra


def file_as_nevr(filename):
    if filename == '-':
        builds = list_or_splitstr(sys.stdin.read())
    else:
        builds = split_file(filename)

    tidied = [tidy_nevra(build) for build in builds]
    ret = {componentize(item): item for item in sorted(tidied)}
    return ret
