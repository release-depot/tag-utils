Overview
========

tag_utils is a collection of tools to assist in comparing
Pungi compose information and Koji tags.

Setup
=====

$ pip install -r requirements.txt .


Usage
=====
$ tag-delta --delta the-tag-1.1 the-tag-1.2

Clean all non-current builds from a candidate tag:
$ tag-cleaner fedora-29-candidate

Tag things builds from a compose over to a target tag
$ tag-over http://path/to/compose/compose_id target-tag-1.2
