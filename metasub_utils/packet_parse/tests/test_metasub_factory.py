"""Test suite for metadata."""

from unittest import TestCase

from metasub_utils.packet_parse import (
    MetaSUBTableFactory,
)


class TestMetaSUBTableFactory(TestCase):
    """Test suite for metadata."""

    def test_build_core_factory(self):
        """Test that we can build a core factory."""
        tabler = MetaSUBTableFactory.core_factory()

    def test_build_air_factory(self):
        """Test that we can build a core factory."""
        tabler = MetaSUBTableFactory.air_factory()

    def test_build_city_factory(self):
        """Test that we can build a core factory."""
        tabler = MetaSUBTableFactory.city_factory('new_york_city', core=True)
