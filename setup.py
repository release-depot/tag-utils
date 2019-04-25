#!/usr/bin/env python
# Copyright (c) 2019, Red Hat, Inc.
#   License: MIT
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


TEST_REQUIRES = ['coverage', 'flake8', 'pytest', 'pytest-datadir', 'tox']

setup(
    name='tag_utils',
    version='0.0.3',
    setup_requires=['pytest-runner'],
    install_requires=['pyyaml'],
    tests_require=TEST_REQUIRES,
    extras_require={'test': TEST_REQUIRES},
    license='MIT',
    description=("tag_utils is a collection of Pungi compose "
                 "and Koji tag functions for release-depot."),
    long_description=readme + '\n\n' + history,
    author='Red Hat',
    author_email='lon@metamorphism.com',
    maintainer='Lon Hohberger',
    maintainer_email='lon@metamorphism.com',
    packages=find_packages(),
    url='http://github.com/release-depot/tag-utils',
    data_files=[("", ["LICENSE"])],
    test_suite='tests',
    zip_safe=False,
    entry_points={
        'console_scripts': ['tag-cleaner = tag_utils.cli.tag_cleaner:main',
                            'tag-delta = tag_utils.cli.tag_delta:main',
                            'tag-over = tag_utils.cli.tag_over:main']
    },
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Utilities'],
)
