#!/usr/bin/env python

import argparse
import subprocess

import koji

from koji_wrapper.tag import KojiTag
from koji_wrapper.base import KojiWrapperBase

from toolchest.rpm.utils import splitFilename
from toolchest.rpm.utils import labelCompare

from tag_utils.koji import latest_package


def builds_package(koji_tag, package):
    if koji_tag.tagged_list is not None and package is not None:
        return [build['nvr'] for build in koji_tag.tagged_list if build['name'] == package]


def untag_it(brew_tag, builds, dry_run=False, verbose=False):

    print("Untagging {0} builds from {1}".format(len(builds), brew_tag))
    if verbose:
        print(builds)

    stride = 10
    builds_to_untag = builds
    while len(builds_to_untag) > 0:
        this_set = builds_to_untag[0:stride]
        builds_to_untag = builds_to_untag[stride:]

        cmd = ['brew', 'untag-build', brew_tag]

        for build in this_set:
            print('Untagging {0}'.format(build))
            cmd.append(build)

        print("calling out to brew...")
        if verbose or dry_run:
            print(cmd)

        if not dry_run:
            subprocess.call(cmd)


def tag_cleaner(args):

    print('attempting to do tag cleanup on {0}'.format(args.brew_tag))

    exclude_components = set(args.exclude.split(','))

    if '-candidate' in args.brew_tag:
        base_tag = args.brew_tag[0:-len('-candidate')]
    elif '-pending' in args.brew_tag:
        base_tag = args.brew_tag[0:-len('-pending')]
    elif '-override' in args.brew_tag:
        base_tag = args.brew_tag[0:-len('-override')]
    else:
        raise Exception("brew tag must be either -candidate, -pending" +
                        " or -override otherwise I don't know what to do")

    candidate_tag = args.brew_tag
    container_tag = base_tag + '-container-released'

    bw = KojiWrapperBase(profile='brew')

    if args.latest:
        released_builds = KojiTag(session=bw, tag=candidate_tag)
    else:
        released_builds = KojiTag(session=bw, tag=base_tag)

    staged_builds = KojiTag(session=bw, tag=candidate_tag)

    released_builds.builds(inherit=False, latest=args.latest)
    staged_builds.builds(inherit=False, latest=False)

    released_containers = None
    dc = []
    try:
        if not args.latest and container_tag:
            released_containers = KojiTag(session=bw, tag=container_tag)
            released_containers.builds(inherit=False)
            dc = released_containers.builds_by_attribute('name')
    except koji.GenericError:
        released_containers = None
        dc = []

    lc = released_builds.builds_by_attribute('name')
    rc = staged_builds.builds_by_attribute('name')

    common = sorted(list((set(lc) & set(rc)) - exclude_components))  # NOQA
    new_build_components = sorted(list((set(rc) - set(lc) - set(dc)) - exclude_components))  # NOQA
    tagged_only_components = sorted(list((set(lc) - set(rc)) - exclude_components))  # NOQA
    tagged_only_containers = sorted(list((set(dc) - set(rc)) - exclude_components))  # NOQA
    common_containers = sorted(list((set(dc) & set(rc)) - exclude_components))  # NOQA

    if args.debug:
        print({'tagged_only': tagged_only_components,
               'new_builds': new_build_components,
               'common': common,
               'common_containers': common_containers,
               'tagged_only_containers': tagged_only_containers})

    builds_to_untag = []
    for c in common:
        rel_build = latest_package(released_builds, c)
        can_builds = builds_package(staged_builds, c)
        if args.debug:
            print('released', rel_build)
            print('-candidate', can_builds)

        if (
                (args.clean_all) and
                (rel_build in can_builds) and
                (rel_build == latest_package(staged_builds, c))
        ):
            if args.debug:
                print("Latest build {0} is released".format(rel_build) +
                      ", untagging them all")
            for build in can_builds:
                builds_to_untag.append(build)
            continue

        for build in can_builds:
            if build == rel_build:
                if not args.latest:
                    if args.debug:
                        print("Latest build {0} is released".format(rel_build))
                    builds_to_untag.append(build)
                else:
                    if args.debug:
                        print("Preserving latest build {0}".format(rel_build))
                continue
            else:
                (ln, lv, lr, le, la) = splitFilename(rel_build)
                (rn, rv, rr, re, ra) = splitFilename(build)

                v = labelCompare((le, lv, lr), (re, rv, rr))
                if v > 0:
                    if args.debug:
                        print("released is newer, untagging {0}".format(build))
                    builds_to_untag.append(build)
                elif v < 0:
                    if args.debug:
                        print("Skipping {0} newer than released".format(build))
                else:
                    if args.debug:
                        print("released equal, untagging {0}".format(build))
                    if not args.latest:
                        builds_to_untag.append(build)

    for c in common_containers:
        if args.debug:
            print('Looking at container {0}'.format(c))

        rel_build = latest_package(released_containers, c)
        can_builds = builds_package(staged_builds, c)
        if args.debug:
            print('released', rel_build)
            print('-candidate', can_builds)

        if (
                (args.clean_all) and
                (rel_build in can_builds) and
                (rel_build == latest_package(staged_builds, c))
        ):
            if args.debug:
                print("Latest build {0} is released".format(rel_build) +
                      ", untagging them all")
            for build in can_builds:
                builds_to_untag.append(build)
            continue

        for build in can_builds:
            if build == rel_build:
                if args.debug:
                    print("Latest build {0} is released".format(rel_build))
                builds_to_untag.append(build)
                continue
            else:
                (ln, lv, lr, le, la) = splitFilename(rel_build)
                (rn, rv, rr, re, ra) = splitFilename(build)

                v = labelCompare((le, lv, lr), (re, rv, rr))
                if v > 0:
                    if args.debug:
                        print("released is newer, untagging {0}".format(build))
                    builds_to_untag.append(build)
                elif v < 0:
                    if args.debug:
                        print("Skipping {0} newer than released".format(build))
                else:
                    if args.debug:
                        print("released equal, untagging {0}".format(build))
                    builds_to_untag.append(build)

    # NOTE: jschlueter 2016-12-16
    # for RH-OSP we have several image builds that use
    # brew image-build-indirection to generate the released images
    # rhosp-director-images ==> director-utility,director-input
    #   director-utility and -input are used to generate overcloud-full
    #   and ironic-python-agent images.  Those images are then embedded
    #   in rhos-director-images.
    # This means we never release director-utility/-input images and they
    # need to be cleaned out of the -candidate tag but we would like to keep
    # last released one around plus any newer than last released
    #
    # add logic to handle director-input/-utility
    # we want to keep corresponding -input and -utility images
    # matching build is:
    # overcloud-full-<VR>
    #    == director-input-<VR>
    #    == director-utility-<VR>
    latest_images = None
    if (
            (('director-input' in rc) or ('director-utility' in rc)) and
            ('overcloud-full' in lc)
    ):
        latest_images = latest_package(released_builds, 'overcloud-full')
        if args.debug:
            if latest_images is not None:
                print('Attempting director-input/utility image cleanup')
            else:
                print('Skipping director-input/utility no overcloud-full found')

    if latest_images is not None:
        VR = latest_images[len('overcloud-full'):]
        keep = ['director-input' + VR, 'director-utility' + VR]

        print("Trying to clean up director-input and director-utility")
        print("Keeping {0} for Released {1}".format(keep, latest_images))
        for c in ['director-input', 'director-utility']:
            for build in builds_package(staged_builds, c):
                if build in keep:
                    continue

                (ln, lv, lr, le, la) = splitFilename(c + VR)
                (rn, rv, rr, re, ra) = splitFilename(build)

                v = labelCompare((le, lv, lr), (re, rv, rr))
                if v > 0:
                    if args.debug:
                        print("released is newer, untagging")
                    builds_to_untag.append(build)

    if len(builds_to_untag) > 0:
        untag_it(candidate_tag, builds_to_untag, dry_run=args.dry_run,
                 verbose=args.debug)
    else:
        print("All Clean. nothing to do for {0}".format(candidate_tag))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--clean-all', action='store_true', default=False,
                        help='clean-all ')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Dry Run - show what we are doing')
    parser.add_argument('brew_tag', help='brew tag to clean')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable additional debugging output')
    parser.add_argument('--exclude', help='components to exclude',
                        type=str, default='')
    parser.add_argument('--latest', action='store_true', default=False,
                        help='Ignore released; clean all-but-latest')

    args = parser.parse_args()

    tag_cleaner(args)


if __name__ == '__main__':
    main()
