#!/usr/bin/env python

import koji_wrapper
from koji_wrapper.base import KojiWrapperBase
from koji_wrapper.tag import KojiTag

from toolchest.rpm.utils import labelCompare
from toolchest.rpm.utils import splitFilename

from tag_utils.common import latest_tagged_as_nevr
from tag_utils.compose import compose_as_nevr


def tag_to_latest_builds(tag):
    if isinstance(tag, str):
        session = KojiWrapperBase(profile='brew')
        koji_tag = KojiTag(tag, session=session)
    elif isinstance(tag, koji_wrapper.tag.KojiTag):
        koji_tag = tag
    else:
        raise ValueError('Expected KojiTag or str')

    if koji_tag.tagged_list is None:
        koji_tag.builds()

    return latest_tagged_as_nevr(koji_tag)


# Automatically resolve input class to dict of:
#   {'n': 'n-e:v-r', 'm': 'm-e:v-r'}
# Supports:
#    - pungi compose
#    - koji tag
def input_to_nevr_dict(inp):
    ret = None

    if isinstance(inp, str):
        if ( inp.startswith('http://') or   # NOQA
             inp.startswith('https://') or  # NOQA
             inp.startswith('/')):
            # fetch compose data
            ret = compose_as_nevr(inp)
        else:
            # fetch koji tag data
            ret = tag_to_latest_builds(inp)
        return ret

    # It might be a list of builds already
    if isinstance(inp, dict):
        return inp

    if isinstance(inp, koji_wrapper.tag.KojiTag):
        return tag_to_latest_builds(inp)

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
def delta(inp_left, inp_right):
    left = input_to_nevr_dict(inp_left)
    right = input_to_nevr_dict(inp_right)

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
    ret['removed'] = removed
    ret['added'] = added
    ret['common'] = common
    ret['downgrades'] = downgrades
    ret['upgrades'] = upgrades

    return ret
