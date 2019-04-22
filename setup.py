#!/usr/bin/env python
"""Setup
"""

__version__ = "0.0.1"

import re
import setuptools


def requires(prefix=''):
    """Retrieve requirements from requirements.txt
    """
    try:
        reqs = map(str.strip, open(prefix + 'requirements.txt').readlines())
        reqs = filter(lambda s: re.match(r'\W', s), reqs)
        return reqs
    except Exception:
        pass
    return []


setuptools.setup(
    name='tag_utils',
    version=__version__,
    description="""tag_utils is a collection of tools to assist in managing
and updating Koji tags""",
    author='Lon Hohberger',
    author_email='lon@metamorphism.com',
    url='http://github/lhh/tag_utils',
    packages=[
        'tag_utils'
    ],
    include_package_data=True,
    install_requires=requires(),
    tests_require=requires(prefix="test-"),
    test_suite='nose.collector',
    entry_points={
        'console_scripts': ['tag-cleaner = tag_utils.tag_cleaner:main',
                            'tag-delta = tag_utils.tag_delta:main',
                            'tag-over = tag_utils.tag_over:main']
    }
)
