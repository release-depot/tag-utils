#!/usr/bin/env python


def latest_package(koji_tag, package):
    """Helper to wrap prior behavior from brewtag"""
    if koji_tag.tagged_list is not None:
        return [build['nvr'] for build in koji_tag.tagged_list if build['name'] == package][0]
    return None
