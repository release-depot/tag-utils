#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys

from toolchest import decor

from tag_utils.common import evr_from_nevr
from tag_utils.delta import delta


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--new', action='store_true', default=False,
                        help='show new packages in output')
    parser.add_argument('--delta', action='store_true', default=False,
                        help='show both new and removed packages in output')
    parser.add_argument('-N', '--no-inherit', action='store_true',
                        default=False,
                        help='Do not use inherit when checking tags')
    parser.add_argument('--skip-same', action='store_true', default=False,
                        help='skip printing entries if they are the same')

    parser.add_argument('left_tag', help='left brew tag for comparison')
    parser.add_argument('right_tag', help='right brew tag for comparison')
    args = parser.parse_args()

    show_new = False
    show_removed = False
    do_inherit = True

    if args.new:
        show_new = True
    if args.delta:
        show_new = True
        show_removed = True
    if args.no_inherit:
        do_inherit = False

    rows, columns = os.popen('stty size', 'r').read().split()
    fw = str(int((int(columns) - 3) / 3))

    delta_info = delta(args.left_tag, args.right_tag, inherit=do_inherit)

    lc = sorted(delta_info['old'].keys())
    rc = sorted(delta_info['new'].keys())
    common = sorted(delta_info['common'].keys())

    lname = os.path.basename(args.left_tag)
    rname = os.path.basename(args.right_tag)

    if sys.stdout.isatty():
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        print(f % ('component', lname, rname))
        print(f % (decor.line('component'), decor.line(lname),
                   decor.line(rname)))
    else:
        print()
        print('component,' + lname + ',' + rname + ',status')

    # Downgrades (normally bad)
    for c in sorted(delta_info['downgrades'].keys()):
        lnevr = delta_info['downgrades'][c]['old']
        rnevr = delta_info['downgrades'][c]['new']

        levr = evr_from_nevr(lnevr)
        revr = evr_from_nevr(rnevr)

        if sys.stdout.isatty():
            f = '%' + fw + 's %s%' + fw + 's %s%' + fw + 's'
            print(f % (c, decor.HILIGHT, levr, decor.NORMAL, revr))
        else:
            if delta_info['downgrades'][c]['rebase']:
                print(f'{c},{levr},{revr},rebase')
            else:
                print(f'{c},{levr},{revr},')

    for c in sorted(delta_info['upgrades'].keys()):
        lnevr = delta_info['upgrades'][c]['old']
        rnevr = delta_info['upgrades'][c]['new']

        levr = evr_from_nevr(lnevr)
        revr = evr_from_nevr(rnevr)

        if sys.stdout.isatty():
            f = '%' + fw + 's %' + fw + 's %s%' + fw + 's%s'
            print(f % (c, levr, decor.HILIGHT, revr, decor.NORMAL))
        else:
            if delta_info['upgrades'][c]['rebase']:
                print(f'{c},{levr},{revr},rebase')
            else:
                print(f'{c},{levr},{revr},')

    if not args.skip_same:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in sorted(delta_info['common'].keys()):
            nevr = delta_info['common'][c]
            evr = evr_from_nevr(nevr)

            if sys.stdout.isatty():
                print(f % (c, evr, evr))
            else:
                print(f'{c},{evr},{evr},')

    if show_new:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in sorted(delta_info['added'].keys()):
            nevr = delta_info['added'][c]
            evr = evr_from_nevr(nevr)
            if sys.stdout.isatty():
                print(f % (c, '---', evr))
            else:
                print(c + ',---,' + evr + ',new')

    if show_removed:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in sorted(delta_info['removed'].keys()):
            nevr = delta_info['removed'][c]
            evr = evr_from_nevr(nevr)

            if sys.stdout.isatty():
                print(f % (c, evr, '---'))
            else:
                print(c + ',' + evr + ',---' + ',removed')

    print()
    print('%d builds in %s' % (len(lc), lname))
    print('%d builds in %s' % (len(rc), rname))

    overlap = len(common) + len(delta_info['upgrades']) + len(delta_info['downgrades'])
    total_pkgs = len(delta_info['added']) + len(delta_info['removed']) + overlap
    print('Overlap: %d packages (%f %%)' % (overlap, float(overlap) / float(total_pkgs) * 100))
    print('Downgrades:', len(delta_info['downgrades']))
    print('Upgrades:', len(delta_info['upgrades']))
    if show_new:
        print('Added Packages:', len(delta_info['added']))
    if show_removed:
        print('Removed Packages:', len(delta_info['removed']))


if __name__ == '__main__':
    main()
