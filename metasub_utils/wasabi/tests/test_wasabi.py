"""Test suite for wasabi."""

from unittest import TestCase
from os import getcwd
from os.path import isfile
from random import randint

from metasub_utils.wasabi import WasabiBucket


class TestWasabi(TestCase):
    """Test suite for wasabi."""

    def test_download_file(self):
        bucket = WasabiBucket()
        local_name = f'{getcwd()}/temp_{randint(0, 1000 * 1000)}'
        bucket.download('metasub/Scripts/downloadem.sh', local_name, False)
        bucket.close()
        self.assertTrue(isfile(local_name))
        self.assertTrue(len(open(local_name).read()) > 0)
