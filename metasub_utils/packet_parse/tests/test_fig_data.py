"""Test suite for figures."""

from unittest import TestCase
from os import environ

from metasub_utils.packet_parse.figs_data import MetaSUBFiguresData

PACKET_DIR = environ['METASUB_DATA_PACKET_DIR']


class TestMetaSUBFiguresData(TestCase):
    """Test suite for metadata."""

    def test_make_data(self):
        MetaSUBFiguresData(PACKET_DIR)
