#!/usr/bin/env python

import compose
import copy
import subprocess


def chunky(stuff, length):
    for i in range(0, len(stuff), length):
        yield stuff[i:i + length]


def main():
    import sys
    argv = sys.argv

    if len(argv) < 4:
        print(f'usage: {argv[0]} baseurl compose_id koji_tag')
        return 1

    rpm_meta = compose.fetch_rpm_metadata(argv[1], argv[2])
    builds = compose.compose_builds(rpm_meta)
    for b in builds:
        print(b)

    tag_over = ['brew', 'tag-pkg', argv[3]]
    chunked_builds = chunky(builds, 10)
    for b in chunked_builds:
        cmd = copy.copy(tag_over)
        cmd.extend(b)
        subprocess.call(cmd)


if __name__ == '__main__':
    main()
