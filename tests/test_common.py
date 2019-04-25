import unittest

from tag_utils import common


class TestTidyNevra(unittest.TestCase):
    def test_normal(self):
        assert common.tidy_nevra('n-0:1-1') == 'n-1-1'

    def test_normal_arch(self):
        assert common.tidy_nevra('n-0:1-1.x86_64') == 'n-1-1.x86_64'

    def test_epoch(self):
        assert common.tidy_nevra('n-1:1-1') == 'n-1:1-1'

    def test_epoch_arch(self):
        assert common.tidy_nevra('n-1:1-1.x86_64') == 'n-1:1-1.x86_64'

    def test_preceding_epoch(self):
        assert common.tidy_nevra('1:n-1-1.x86_64') == 'n-1:1-1.x86_64'

    def test_preceding_zero_epoch(self):
        assert common.tidy_nevra('0:n-1-1.x86_64') == 'n-1-1.x86_64'


class TestEvrFromNevr(unittest.TestCase):
    def test_normal(self):
        assert common.evr_from_nevr('n-0:1-1') == '0:1-1'

    def test_no_epoch(self):
        assert common.evr_from_nevr('n-1-1') == '1-1'

    def test_long_name(self):
        assert common.evr_from_nevr('lots-of-dashes-in-name-1-1') == '1-1'

    def test_arch(self):
        assert common.evr_from_nevr('n-1.1-1.x86_64') == '1.1-1.x86_64'
