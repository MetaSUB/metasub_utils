import pandas as pd
import networkx as nx
import warnings
import numpy as np
import microbe_directory as md

from capalyzer.packet_parser import DataTableFactory, NCBITaxaTree, annotate_taxa, TaxaTree
from capalyzer.packet_parser.data_utils import group_small_cols
from capalyzer.packet_parser.diversity_metrics import (
    shannon_entropy, richness, chao1, rarefaction_analysis
)
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, cophenet, leaves_list
from scipy.spatial.distance import squareform, pdist, jensenshannon

from os.path import join
from metasub_utils.packet_parse import MetaSUBTableFactory
from capalyzer.packet_parser.experimental import umap
from capalyzer.packet_parser.data_utils import group_small_cols
from capalyzer.packet_parser.normalize import proportions, prevalence
from scipy.cluster.hierarchy import fcluster
from matplotlib import pyplot as plt

from capalyzer.constants import MICROBE_DIR


def to_title(el):
    sel = str(el)
    if not el:
        return el
    tkns = sel.split('_')
    tkns = [tkn[0].upper() + tkn[1:] for tkn in tkns]
    return ' '.join(tkns)


class MetaSUBFiguresData:

    def __init__(self, packet_dir, ncbi_tree=None):
        self.tabler = DataTableFactory(packet_dir, metadata_tbl='metadata/complete_metadata.csv')
        self.tabler.metadata['continent'] = self.tabler.metadata['continent'].map(to_title)
        self.meta = self.tabler.metadata
        self._ncbi_tree = ncbi_tree

    @property
    def ncbi_tree(self):
        if self._ncbi_tree is None:
            self._ncbi_tree = NCBITaxaTree.parse_files()
        return self._ncbi_tree

    @property
    def wide_taxa(self):
        return self.build_wide_taxonomy()

    @property
    def wide_taxa_rel(self):
        return proportions(self.wide_taxa)

    @property
    def wide_phyla(self):
        return self.tabler.taxonomy(rank='phylum')

    @property
    def wide_phyla_rel(self):
        return proportions(self.wide_phyla)

    @property
    def function_groups(self):
        return self.build_functional_groups()

    @property
    def amrs(self):
        return self.build_amrs()

    @property
    def emp(self):
        return self.build_soil_comparison()

    @property
    def hmp(self):
        return self.build_hmp_comparison()

    @property
    def rps(self):
        return self.build_rps()
    

    def build_soil_comparison(self):
        emp = pd.read_csv(
            self.tabler.packet_dir + '/other/metasub_soil_mash_comparison.csv',
            names=['sample_name', 'emp_sample', 'jaccard', 'pval', 'hashes']
        )
        emp = emp.loc[emp['sample_name'].isin(self.meta.index)]
        emp['continent'] = [self.meta.loc[sn]['continent'] for sn in emp['sample_name']]
        # emp['surface'] = [self.meta.loc[sn]['surface_ontology_fine'] for sn in emp['sample_name']]
        emp = emp.dropna()
        return emp

    def build_hmp_comparison(self):
        hmp = pd.read_csv(
            self.tabler.packet_dir + '/other/metasub_hmp_mash_comparison.csv',
            names=['sample_name', 'hmp_sample', 'hmp_site_fine', 'body_site', 'jaccard', 'pval', 'hashes']
        )
        hmp = hmp.loc[hmp['sample_name'].isin(self.meta.index)]
        hmp['continent'] = [self.meta.loc[sn]['continent'] for sn in hmp['sample_name']]
        # hmp['surface'] = [self.meta.loc[sn]['surface_ontology_fine'] for sn in hmp['sample_name']]
        hmp = hmp.dropna()
        return hmp

    def build_wide_taxonomy(self):
        """Return a pandas df with species in columns, samples in rows. Values are read counts."""
        return self.tabler.taxonomy()

    def build_functional_groups(self):
        paths = self.tabler.pathways()
        mypaths = paths[[el for el in paths.columns if 'unclassified' not in el and 'UNINTEG' not in el]]
        co = mypaths.corr()
        co['path_1'] = co.index
        co = co.melt(id_vars=['path_1'])
        co.columns = ['path_1', 'path_2', 'value']
        co = co.query('value > = 0.75')

        def wordcloud(paths):
            tbl = {}
            for path in paths:
                for word in path.split():
                    tbl[word] = 1 + tbl.get(word, 0)
            otbl = sorted([(k, v) for k, v in tbl.items()], key=lambda x: -x[1])
            tbl = [k for k, v in otbl if v > 1]
            tbl = [k for k in tbl if len(k) > 3 and 'PWY' not in k]
            if len(tbl) < 3:
                tbl = [k for k, _ in otbl if 'PWY' not in k]
            return tbl[:10]

        G = nx.Graph()
        for _, row in co.iterrows():
            G.add_edge(row['path_1'], row['path_2'])

        n, p = 0, 0
        comps = [comp for comp in nx.connected_components(G) if len(comp) > 1]
        wcs = {f'COMP_{i}': (comp, wordcloud(comp)) for i, comp in enumerate(comps)}
        for name, (comp, wc) in wcs.items():
            if len(comp) == 1:
                continue
            n += 1
            p += len(comp)
            these_paths = mypaths[comp].sum(axis=1)
            mypaths = mypaths.drop(columns=comp)
            mypaths[name] = these_paths

        mypaths = (mypaths.T / mypaths.T.sum()).T.dropna()
        low_abundance_paths = mypaths.columns[mypaths.mean() < 0.01]
        low_abundance = mypaths[low_abundance_paths].sum(axis=1)
        mypaths = mypaths.drop(columns=low_abundance_paths)
        mypaths['Other'] = low_abundance

        cats = {
            'PWY-3781: aerobic respiration I (cytochrome c)': 'Aerobic Respiration',
            'COMP_0': 'Fatty Acid Biosynthesis',
            'COMP_1': 'L-arginine Biosynthesis',
            'COMP_2': 'Pyrimidine Biosynthesis',
            'COMP_3': 'Glycerol Biosynthesis',
            'COMP_8': 'Glycolysis',
            'COMP_6': 'Folate Biosynthesis',
            'COMP_10': 'Methionine Biosynthesis',
            'COMP_11': 'Purine Biosynthesis',
        }
        foo = mypaths.rename(columns=cats)
        foo['sample'] = foo.index
        foo['continent'] = self.tabler.metadata['continent']
        foo['continent'] = [str(el) for el in foo['continent']]
        foo = foo.melt(id_vars=['sample', 'continent'])
        foo = foo.dropna()

        return foo

    def build_amrs(self):
        """TODO: REVIEW."""
        amrs = self.tabler.amrs(kind='class', remove_zero_rows=False).drop(columns=['Elfamycins']).dropna()
        amrs = (amrs.T / (amrs.T.sum() + 0.000001)).T
        return amrs

    def build_unclassified(self):
        non_human_unkown = (rps['unknown'] / (1 - rps['host'])).mean()
        non_human_known = 1 - non_human_unkown
        non_human_blast_nt_aligned = (self.tabler.csv_in_dir('other/nt_aligned_counts.csv') / 10000)

    def build_rps(self):
        rps = self.tabler.read_props()
        rps['continent'] = self.tabler.metadata['continent']
        # rps['surface'] = self.tabler.metadata['surface_ontology_fine']
        rps = rps.dropna()
        return rps
