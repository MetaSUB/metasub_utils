"""Test suite for figures."""

import unittest
from unittest import TestCase
from os import environ

from metasub_utils.packet_parse.figs import MetaSUBFigures

unittest.TestLoader.sortTestMethodsUsing = None

PACKET_DIR = environ['METASUB_DATA_PACKET_DIR']
myfigs = MetaSUBFigures(PACKET_DIR)


class TestMetaSUBTables(TestCase):
    """Test suite for metadata."""

    _multiprocess_shared_ = True

    def test_tbl1(self):
        myfigs.tbl1()
