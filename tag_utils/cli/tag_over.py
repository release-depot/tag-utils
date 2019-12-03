#!/usr/bin/env python
#
# TODO: use koji_wrapper to tag things

import copy
import subprocess

from toolchest.rpm.utils import drop_epoch
from tag_utils.delta import delta


def chunky(stuff, length):
    for i in range(0, len(stuff), length):
        yield stuff[i:i + length]


def main():
    import sys
    argv = sys.argv
    missing = False
    display = False
    dest_tag = None

    if len(argv) < 3:
        print(f'usage: {argv[0]} [--missing|--dest desttag] tag_or_compose tag')
        print()
        print('Compare \"tag_or_compose\" with \"tag\" and tag anything that would be')
        print('an upgrade to \"tag\".  If \"desttag\" is specified, tag packages')
        print('to \"desttag\" instead of \"tag\".')
        return 1

    # XXX switch to argparser if we get any more
    while argv[1].startswith('--'):
        arg = argv.pop(1)
        if arg == '--print':
            display = True
        if arg == '--missing':
            missing = True
        if arg == '--dest':
            dest_tag = argv.pop(1)

    if not dest_tag:
        dest_tag = argv[2]

    delta_info = delta(argv[1], argv[2])

    # This could be done as a list generation, but it becomes less readable
    builds = []
    for comp in delta_info['downgrades']:
        builds.append(drop_epoch(delta_info['downgrades'][comp]['old']))
    if missing:
        for comp in delta_info['removed']:
            builds.append(drop_epoch(delta_info['removed'][comp]))

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
