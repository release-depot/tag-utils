#!/usr/bin/env python

from toolchest.rpm.utils import splitFilename


def tidy_nevra(nevra):
    (n, v, r, e, a) = splitFilename(nevra)
    if e != 0 and e != '' and e != '0':
        v = f'{e}:{v}'

    nevra = '-'.join([x for x in [n, v, r] if x != ''])

    if a:
        nevra = f'{nevra}.{a}'
    return nevra


# Note - doesn't work with preceding epoch!
def evr_from_nevr(nevr):
    return '-'.join(nevr.rsplit('-', 2)[1:])
