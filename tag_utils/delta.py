#!/usr/bin/env python

import os

import koji_wrapper
from koji_wrapper.base import KojiWrapperBase
from koji_wrapper.tag import KojiTag

from toolchest.rpm.utils import splitFilename
from toolchest.rpm.utils import labelCompare
from toolchest.rpm.utils import componentize

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


# Automatically resolve input class to list of n-e:v-r
# Supports:
#    - pungi compose
#    - koji tag
def input_to_list(inp):
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
    if isinstance(inp, list):
        return inp

    if isinstance(inp, koji_wrapper.tag.KojiTag):
        return tag_to_latest_builds(inp)

    raise ValueError('Unhandled type: ' + str(type(inp)))
