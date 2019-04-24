#!/usr/bin/env python


def koji_build_to_nevr(build):
    epoch_str = ''
    if build['epoch'] is not None:
        epoch_str = str(build['epoch']) + ':'
    name = build['name']
    version = build['version']
    release = build['release']

    return f'{name}-{epoch_str}{version}-{release}'


def latest_package_nevr(koji_tag, package):
    """Helper to wrap prior behavior from brewtag"""
    if koji_tag.tagged_list is not None:
        for build in koji_tag.tagged_list:
            if build['name'] == package:
                return koji_build_to_nevr(build)
    return None


def latest_tagged_as_nevr(koji_tag):
    # Koji reports latest tagged version of a component
    # first, so we can short-circuit after we get the first
    # one
    ret = {}
    for build in koji_tag.tagged_list:
        if build['name'] in ret:
            continue
        ret[build['name']] = koji_build_to_nevr(build)
    return ret


def latest_package(koji_tag, package):
    """Helper to wrap prior behavior from brewtag"""
    if koji_tag.tagged_list is not None:
        for build in koji_tag.tagged_list:
            if build['name'] == package:
                return build['nvr']
    return None
