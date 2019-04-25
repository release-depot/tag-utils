#!/usr/bin/env python

import koji_wrapper
from koji_wrapper.base import KojiWrapperBase
from koji_wrapper.tag import KojiTag

from toolchest.rpm.utils import labelCompare
from toolchest.rpm.utils import splitFilename

from .koji import latest_tagged_as_nevr
from .compose import compose_as_nevr

__koji_session = None


def tag_to_latest_builds(tag, **kwargs):
    global __koji_session
    inherit = False

    if 'session' in kwargs:
        __koji_session = kwargs['session']
    if 'inherit' in kwargs:
        inherit = kwargs['inherit']

    if isinstance(tag, str):
        if __koji_session is None:
            __koji_session = KojiWrapperBase(profile='brew')
        if __koji_session is None:
            raise Exception('Could not connect to koji')
        koji_tag = KojiTag(tag, session=__koji_session)
    elif isinstance(tag, koji_wrapper.tag.KojiTag):
        koji_tag = tag
    else:
        raise ValueError('Expected KojiTag or str')

    if koji_tag.tagged_list is None:
        koji_tag.builds(inherit=inherit)

    return latest_tagged_as_nevr(koji_tag)


# Automatically resolve input class to dict of:
#   {'n': 'n-e:v-r', 'm': 'm-e:v-r'}
# Supports:
#    - pungi compose
#    - koji tag
def input_to_nevr_dict(inp, **kwargs):
    ret = None

    if isinstance(inp, str):
        if ( inp.startswith('http://') or   # NOQA
             inp.startswith('https://') or  # NOQA
             inp.startswith('/')):
            # fetch compose data
            ret = compose_as_nevr(inp)
        else:
            # fetch koji tag data
            ret = tag_to_latest_builds(inp, **kwargs)
        return ret

    # It might be a list of builds already
    if isinstance(inp, dict):
        return inp

    if isinstance(inp, koji_wrapper.tag.KojiTag):
        return tag_to_latest_builds(inp, **kwargs)

    raise ValueError('Unhandled type: ' + str(type(inp)))


# Returns:
#   - removed: components+builds which are in left, but
#              not in right
#   - added: components (and corresponding builds) which are
#            in right, but not in left
#   - common: components (and builds) which are equal between
#             left and right
#   - downgrades: components/builds where the n-e:v-r has decreased
#                 from left to right
#   - upgrades: components/builds where the n-e:v-r has increased
#               from left to right
def delta(inp_left, inp_right, **kwargs):
    left = input_to_nevr_dict(inp_left, **kwargs)
    right = input_to_nevr_dict(inp_right, **kwargs)

    lc = set(left.keys())
    rc = set(right.keys())

    removed_comps = sorted(list(lc - rc))
    removed = {}
    for comp in removed_comps:
        removed[comp] = left[comp]

    added_comps = sorted(list(rc - lc))
    added = {}
    for comp in added_comps:
        added[comp] = right[comp]

    common_comps = sorted(list(lc & rc))
    common = {}
    downgrades = {}
    upgrades = {}
    # Break this one up in a more granular fashion
    for comp in common_comps:
        lnevr = left[comp]
        rnevr = right[comp]

        (ln, lv, lr, le, la) = splitFilename(lnevr)
        (rn, rv, rr, re, ra) = splitFilename(rnevr)

        rebase = False
        if lv != rv:
            rebase = True
        ret = labelCompare((le, lv, lr), (re, rv, rr))
        if ret > 0:
            downgrades[comp] = {'old': lnevr, 'new': rnevr, 'rebase': rebase}
        elif ret < 0:
            upgrades[comp] = {'old': lnevr, 'new': rnevr, 'rebase': rebase}
        else:
            common[comp] = lnevr

    ret = {}
    ret['old'] = left
    ret['new'] = right
    ret['removed'] = removed
    ret['added'] = added
    ret['common'] = common
    ret['downgrades'] = downgrades
    ret['upgrades'] = upgrades

    return ret
