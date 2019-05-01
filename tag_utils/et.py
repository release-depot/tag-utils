
from .koji import koji_build_to_nevr
import errata_tool.release
from errata_tool.erratum import Erratum
from errata_tool.connector import ErrataConnector


ADVISORY_STATES = ('NEW_FILES', 'QE', 'REL_PREP', 'PUSH_READY')
RELEASE_GROUP_SEARCH_PATH = '/api/v1/releases' + \
        '?filter[is_active]=true&filter[enabled]=true&filter[name]={}'
ADVISORY_SEARCH_PATH = '/errata/errata_for_release/{}.json'

def get_advisory_list(errata_tool_release):
    print('Finding unshipped advisories in {}...'.format(errata_tool_release))
    et = ErrataConnector()
    release_group_search = et._get(
            RELEASE_GROUP_SEARCH_PATH.format(errata_tool_release))
    release_group_ids = []
    for release_group in release_group_search['data']:
        release_group_ids.append(release_group['id'])
    print('  Potential release group IDs (using first):',
          ' '.join(map(str, release_group_ids)))
    advisory_search = et._get(
            ADVISORY_SEARCH_PATH.format(release_group_ids[0]))
    advisory_ids = set()
    for advisory_result in advisory_search:
        if advisory_result['status'] in ADVISORY_STATES:
            advisory_ids.add(advisory_result['id'])
    print('  Advisories in release group {}:'.format(release_group_ids[0]),
          ' '.join(map(str, advisory_ids)))
    return [Erratum(errata_id=advisory_id) for advisory_id in advisory_ids]


def get_build_for_release(release_name_or_id, koji_session):
    release_builds = {}

    print('got in "{0}"'.format(release_name_or_id))
    try:
        rel = errata_tool.release.Release(id=int(release_name_or_id))
        advisories = [i for i in rel.advisories() if i["status"] not in ('SHIPPED_LIVE', 'DROP_NO_SHIP')]
        advisory_list = [Erratum(errata_id=i['id']) for i in advisories]
        print( ("Got list of advisories:", advisories))
    except ValueError:
        advisory_list = get_advisory_list(release_name_or_id)

    check_list = []
    all_builds = set()
    for advisory in advisory_list:
        print('\nFetching builds for {} "{}"'.format(
            advisory.errata_name, advisory.synopsis))
        for release, builds in advisory.errata_builds.items():
            print('  {}: {}'.format(release, ' '.join(builds)))
            all_builds |= set(builds)

    return_data = {}
    for build in all_builds:
        build_data = koji_session.build(build)
        return_data[build_data['name']] = koji_build_to_nevr(build_data)

    return return_data
