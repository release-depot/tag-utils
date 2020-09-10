#!/usr/bin/env python
#
# TODO: use koji_wrapper to tag things

import copy
import subprocess
import argparse

from toolchest.rpm.utils import drop_epoch
from tag_utils.delta import delta
from koji_wrapper.tag import KojiTag
from koji_wrapper.base import KojiWrapperBase


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print', help='Print which packages would be tagged, but don\'t tag them.', action='store_true')
    parser.add_argument('--missing', help='Tag all packages from src_tag, even if the package NVRs match what is in compare_tag.', action='store_true')
    parser.add_argument('--dest', help='Specify a different destination tag than compare_tag.', default=None)
    parser.add_argument('src_tag', help='Tag to source new builds from.')
    parser.add_argument('compare_tag', help='Tag to compare against for updates.')
    return parser.parse_args()


def chunky(stuff, length):
    for i in range(0, len(stuff), length):
        yield stuff[i:i + length]


def main():

    args = get_args()

    if not args.src_tag and not args.compare_tag:
        return 1

    missing = args.missing
    display = args.print
    dest_tag = args.dest
    src_tag = args.src_tag
    compare_tag = args.compare_tag

    if not dest_tag:
        dest_tag = args.compare_tag

    delta_info = delta(src_tag, compare_tag)

    # This could be done as a list generation, but it becomes less readable
    builds = []
    for comp in delta_info['downgrades']:
        builds.append(drop_epoch(delta_info['downgrades'][comp]['old']))
    if missing:
        for comp in delta_info['removed']:
            builds.append(drop_epoch(delta_info['removed'][comp]))

    # if we're tagging somewhere else, avoid dup tagging
    # Search all builds, not just latest
    if dest_tag != compare_tag:
        brew = KojiWrapperBase(profile='brew')
        t = KojiTag(session=brew, tag=dest_tag)
        nvrs = [b['nvr'] for b in t.builds()]
        b = set(builds) & set(nvrs)
        builds = list(set(builds) - b)

    # Simply print what we'd tag
    if display:
        for b in builds:
            print(b)
        return

    tag_over = ['brew', 'tag-pkg', dest_tag]
    chunked_builds = chunky(builds, 10)
    for b in chunked_builds:
        cmd = copy.copy(tag_over)
        cmd.extend(b)
        subprocess.call(cmd)


if __name__ == '__main__':
    main()
