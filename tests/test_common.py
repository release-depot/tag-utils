import unittest

from tag_utils import common


class TestTidyNevra(unittest.TestCase):
    def test_normal(self):
        assert common.tidy_nevra('n-0:1-1') == 'n-1-1'
