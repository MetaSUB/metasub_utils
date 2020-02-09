"""Test suite for figures."""

import unittest
from unittest import TestCase
from os import environ

from metasub_utils.packet_parse.figs import MetaSUBFigures

unittest.TestLoader.sortTestMethodsUsing = None

PACKET_DIR = environ['METASUB_DATA_PACKET_DIR']
myfigs = MetaSUBFigures(PACKET_DIR)


class TestMetaSUBFigures(TestCase):
    """Test suite for metadata."""

    _multiprocess_shared_ = True

    def test_tbl1(self):
        myfigs.tbl1()

    def test_fig1_prevalence_curve(self):
        myfigs.fig1_prevalence_curve()

    def test_fig1_major_taxa_curves(self):
        myfigs.fig1_major_taxa_curves()

    def test_fig1_species_rarefaction(self):
        myfigs.fig1_species_rarefaction()

    def test_fig1_reference_comparisons(self):
        myfigs.fig1_reference_comparisons()

    def test_fig1_fraction_unclassified(self):
        myfigs.fig1_fraction_unclassified()

    def test_fig2_umap(self):
        myfigs.fig2_umap()

    def test_fig2_region_blocks(self):
        myfigs.fig2_region_blocks()

    def test_fig2_pca_flows(self, n_pcs=100):
        myfigs.fig2_pca_flows()

    def test_fig5_amr_cooccur(self):
        myfigs.fig5_amr_cooccur()

    def test_fig5_amr_richness_by_city(self):
        myfigs.fig5_amr_richness_by_city()

    def test_fig5_amr_rarefaction(self):
        myfigs.fig5_amr_rarefaction()
