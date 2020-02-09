"""Test suite for figures."""

import unittest
from unittest import TestCase
from os import environ

from metasub_utils.packet_parse.figs import MetaSUBFigures

unittest.TestLoader.sortTestMethodsUsing = None

PACKET_DIR = environ['METASUB_DATA_PACKET_DIR']
myfigs = MetaSUBFigures(PACKET_DIR)


class TestMetaSUBFigures2(TestCase):
    """Test suite for metadata."""

    _multiprocess_shared_ = True

    def test_fig2_umap(self):
        myfigs.fig2_umap()

    def test_fig2_region_blocks(self):
        myfigs.fig2_region_blocks()

    def test_fig2_pca_flows(self, n_pcs=100):
        myfigs.fig2_pca_flows()
