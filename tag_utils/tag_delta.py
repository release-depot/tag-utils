#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import sys

from toolchest import decor
from toolchest.rpm.utils import splitFilename
from toolchest.rpm.utils import labelCompare

from koji_wrapper.tag import KojiTag
from koji_wrapper.base import KojiWrapperBase

from tag_utils.common import latest_package


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

    upgrades = 0
    downgrades = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    fw = str(int((int(columns)-3)/3))

    bw = KojiWrapperBase(profile='brew')

    ltag = KojiTag(tag=args.left_tag, session=bw)
    rtag = KojiTag(tag=args.right_tag, session=bw)

    ltag.builds(inherit=do_inherit, latest=True)
    rtag.builds(inherit=do_inherit, latest=True)

    lc = ltag.builds_by_attribute('name')
    rc = rtag.builds_by_attribute('name')
    common = sorted(list(set(lc) & set(rc)))
    new_components = sorted(list(set(rc) - set(lc)))
    old_components = sorted(list(set(lc) - set(rc)))

    print('%d builds in %s' % (len(lc), str(ltag.tag)))
    print('%d builds in %s' % (len(rc), str(rtag.tag)))
    print('Overlap: %d packages (%f %%)' % (len(common),
                                            float(len(common)) /
                                            float(len(lc)) * 100))
    if show_new:
        print('New Packages:', len(new_components))
    if show_removed:
        print('Removed Packages:', len(old_components))

    if sys.stdout.isatty():
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        print(f % ('component', str(ltag.tag), str(rtag.tag)))
        print(f % (decor.line('component'), decor.line(str(ltag.tag)),
                   decor.line(str(rtag.tag))))
    else:
        print()
        print('component,' + str(ltag.tag) + ',' + str(rtag.tag) + ',status')

    for c in common:
        lnvr = latest_package(ltag, c)
        rnvr = latest_package(rtag, c)
        (ln, lv, lr, le, la) = splitFilename(lnvr)
        (rn, rv, rr, re, ra) = splitFilename(rnvr)

        lvr = lv + '-' + lr
        rvr = rv + '-' + rr
        rebase = False
        v = labelCompare((le, lv, lr), (re, rv, rr))
        if v < 0 and rv != lv:
            rebase = True

        if sys.stdout.isatty():
            if v > 0:
                f = '%' + fw + 's %s%' + fw + 's %s%' + fw + 's'
                print(f % (c, decor.HILIGHT, lvr, decor.NORMAL, rvr))
                downgrades = downgrades + 1
            elif v < 0:
                f = '%' + fw + 's %' + fw + 's %s%' + fw + 's%s'
                print(f % (c, lvr, decor.HILIGHT, rvr, decor.NORMAL))
                upgrades = upgrades + 1
            elif not args.skip_same:
                f = '%' + fw + 's %' + fw + 's %' + fw + 's'
                print(f % (c, lvr, rvr))
        else:
            if args.skip_same and v == 0:
                continue

            status = ','
            if rebase is True:
                status = ',rebase'
            print(c + ',' + lvr + ',' + rvr + status)

    if show_new:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in new_components:
            rnvr = latest_package(rtag, c)
            (rn, rv, rr, re, ra) = splitFilename(rnvr)
            rvr = rv + '-' + rr
            if sys.stdout.isatty():
                print(f % (c, '---', rvr))
            else:
                print(c + ',---,' + rvr + ',new')

    if show_removed:
        f = '%' + fw + 's %' + fw + 's %' + fw + 's'
        for c in old_components:
            lnvr = latest_package(ltag, c)
            (ln, lv, lr, le, la) = splitFilename(lnvr)
            lvr = lv + '-' + lr
            if sys.stdout.isatty():
                print(f % (c, lvr, '---'))
            else:
                print(c + ',' + lvr + ',---' + ',removed')

    print()
    print('%d builds in %s' % (len(lc), str(ltag.tag)))
    print('%d builds in %s' % (len(rc), str(rtag.tag)))
    print('Overlap: %d packages (%f %%)' % (len(common),
                                            float(len(common)) /
                                            float(len(lc)) * 100))
    print('Downgrades:', downgrades)
    print('Upgrades:', upgrades)
    if show_new:
        print('New Packages:', len(new_components))
    if show_removed:
        print('Removed Packages:', len(old_components))


if __name__ == '__main__':
    main()
