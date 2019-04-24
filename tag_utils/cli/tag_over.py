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

    if len(argv) < 3:
        print(f'usage: {argv[0]} tag_or_compose target_tag')
        return 1

    delta_info = delta(argv[1], argv[2])

    # This could be done as a list generation, but it becomes less readable
    builds = []
    for comp in delta_info['downgrades']:
        builds.append(drop_epoch(delta_info['downgrades'][comp]['old']))

    tag_over = ['brew', 'tag-pkg', argv[2]]
    chunked_builds = chunky(builds, 10)
    for b in chunked_builds:
        cmd = copy.copy(tag_over)
        cmd.extend(b)
        subprocess.call(cmd)


if __name__ == '__main__':
    main()
