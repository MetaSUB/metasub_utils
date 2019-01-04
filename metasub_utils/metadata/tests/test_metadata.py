"""Test suite for metadata."""

from unittest import TestCase
from os.path import isfile
from random import randint

from metasub_utils.metadata import (
    get_complete_metadata,
    get_samples_from_city,
)


class TestMetadata(TestCase):
    """Test suite for metadata."""

    def test_download_metadata(self):
        """Test that we can get complete metadata table."""
        metadata_tbl = get_complete_metadata()
        self.assertTrue(metadata_tbl.shape[0])
        self.assertTrue(metadata_tbl.shape[1])

    def test_get_samples_from_city(self):
        """Test that we get some sample names from a city (assume correct)."""
        sample_names = get_samples_from_city('paris')
        self.assertTrue(sample_names)
