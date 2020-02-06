import pandas as pd
import networkx as nx
import warnings
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches
import microbe_directory as md

from capalyzer.packet_parser import DataTableFactory, NCBITaxaTree, annotate_taxa, TaxaTree
from capalyzer.packet_parser.data_utils import group_small_cols
from capalyzer.packet_parser.diversity_metrics import shannon_entropy, richness, chao1
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, cophenet, leaves_list
from scipy.spatial.distance import squareform, pdist, jensenshannon

from os.path import join
from metasub_utils.packet_parse import MetaSUBTableFactory
from capalyzer.packet_parser.experimental import umap
from capalyzer.packet_parser.data_utils import group_small_cols
from capalyzer.packet_parser.normalize import proportions, prevalence
from plotnine import *
from scipy.cluster.hierarchy import fcluster
from matplotlib import pyplot as plt

from capalyzer.constants import MICROBE_DIR


class MetaSUBFiguresData:

    def __init__(self, packet_dir, ncbi_tree=None):
        self.tabler = DataTableFactory(packet_dir, metadata_tbl='metadata/complete_metadata.csv')
        self.meta = self.tabler.metadata
        if not ncbi_tree:
            ncbi_tree = NCBITaxaTree.parse_files()

        self.wide_taxa = self.build_wide_taxonomy()
        self.wide_phyla_rel = None  # TODO
        # TODO index of metadata must == index of all tables
        self.function_groups = self.build_functional_groups()

        self.amrs = self.build_amrs()

    @property
    def wide_taxa_rel(self):
        """Give a wide taxa table with values as relative abundances."""
        pass

    def build_wide_taxonomy(self):
        """Return a pandas df with species in columns, samples in rows. Values are read counts."""

    def build_functional_groups(self):
        paths = core_tabler.pathways()
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
        foo['continent'] = core_tabler.metadata['continent']
        foo['continent'] = [str(el) for el in foo['continent']]
        foo = foo.melt(id_vars=['sample', 'continent'])
        foo = foo.dropna()

        return foo

    def build_amrs(self):
        """TODO: REVIEW."""
        amrs = self.tabler.amrs(kind='class', remove_zero_rows=False).drop(columns=['Elfamycins']).dropna()
        amrs = (amrs.T / (amrs.T.sum() + 0.000001)).T
        return amrs


class MetaSUBFigures(MetaSUBFiguresData):

    def fig1(self, N=75):
        """Figure showing the major taxa found in the metasub data."""
        return [
            self.fig1_core_taxa_tree(),
            self.fig1_prevalence_curve(),
            self.fig1_major_taxa_curves(N=N),
            self.fig1_species_rarefaction(),
            self.fig1_reference_comparisons(),
            self.fig1_fraction_unclassified(),
        ]

    def fig1_core_taxa_tree(self):
        """Return an ETE tree showing core taxa with annotations."""

    def fig1_prevalence_curve(self):
        """Return a P9 figure showing the distribution of species prevalences."""
        prev = pd.DataFrame({
            'total': prevalence(self.wide_taxa),
            'city': self.wide_taxa.groupby(by=self.meta['city']).apply(prevalence).mean(axis=0),
        })
        prev['taxa'] = prev.index
        prev_flat = prev.melt(id_vars='taxa')
        plot = (
            ggplot(prev_flat, aes(x='value', color='variable', fill='variable')) +
                geom_density(size=2, alpha=0.2) +
                theme_minimal() +
                xlab('Species Prevalence') +
                ylab('Density') +
                geom_vline(xintercept=0.25, color='black') +
                geom_vline(xintercept=0.70, color='black') +
                geom_vline(xintercept=0.95, color='black') +
                annotate(geom='label', x=0.65, y=2.9, label="Sub-Core 70-95% (1,084)", size=10) +
                annotate(geom='label', x=0.33, y=3.5, label="Peripheral, < 25% (2,466)", size=10) +
                annotate(geom='label', x=0.78, y=3.2, label="Core > 95% (61)", size=10) +
                scale_color_brewer(palette="Set1", direction=-1) +
                scale_fill_brewer(palette="Set1", direction=-1) +
                theme(
                    text=element_text(size=50),
                    axis_text_x=element_text(angle=0, hjust=1),
                    legend_position='none',
                )
        )
        return plot

    def fig1_major_taxa_curves(N=75):
        """Return two P9 panels showing prevalence and abundance distributions of major taxa."""
        taxa = self.wide_taxa_rel
        city = taxa.groupby(by=self.meta['city']).median()

        top_taxa = taxa.mean().sort_values(ascending=False)[:N].index
        taxa, city = 1000 * 1000 * taxa[top_taxa], 1000 * 1000 * city[top_taxa]
        taxa_prev, city_prev = prevalence(taxa), prevalence(city)

        taxa_mean, taxa_kurtosis, taxa_sd = taxa.mean(), taxa.kurtosis(), taxa.std()

        def add_stats(taxon):
            m, k, sd = taxa_mean[taxon], taxa_kurtosis[taxon], taxa_sd[taxon]
            return f'{taxon} ({m // 1000:.0f}k, {sd // 1000:.0f}k, {k:.0f})'

        taxa.columns = taxa.columns.apply(add_stats)
        city.columns = city.columns.apply(add_stats)

        taxa, city = taxa.melt(), city.melt()
        taxa['kind'] = 'All Samples'
        city['kind'] = 'City Median'
        both = pd.concat([taxa, city])
        abund = (
            ggplot(both, aes(x='value', color='kind')) +
                geom_density(size=0.5) +
                facet_grid('variable~.', scales="free_y") +
                theme_minimal() +
                ylab('Density') +
                xlab('Abundance (PPM)') +
                scale_x_log10() +
                scale_color_brewer(palette="Set1") +
                labs(color="") +
                theme(
                    axis_text_x=element_text(angle=0, hjust=1),
                    axis_text_y=element_blank(),
                    strip_text_y=element_text(angle=0, hjust=0),
                    text=element_text(size=15),
                    panel_grid_major_x=element_line(colour="grey", size=0.75),
                    panel_grid_major_y=element_blank(),
                    panel_grid_minor=element_blank(),
                    legend_position='bottom',
                )
        )
        taxa_prev, city_prev = taxa_prev.melt(), city_prev.melt()
        taxa_prev['kind'] = 'All Samples'
        city_prev['kind'] = 'City Median'
        both_prev = pd.concat([taxa_prev, city_prev])
        prev = (
            ggplot(both_prev, aes(x='kind', y='value', fill='kind')) +
                geom_col() +
                facet_grid('taxon~.', scales="free_y") +
                theme_minimal() +
                ylab('Prevalence') +
                scale_fill_brewer(palette="Set1") +
                labs(color="") +
                coord_flip() +
                scale_y_continuous(breaks=c(0.1, 0.5, 1)) +
                theme(
                    axis_text_x=element_text(angle=0, hjust=1),
                    axis_text_y=element_blank(),
                    axis_title_y=element_blank(),
                    strip_text_y=element_blank(),
                    text=element_text(size=15),
                    panel_grid_major=element_blank(),
                    legend_position='bottom'
                )
        )
        return abund, prev

    def fig1_species_rarefaction(self):
        """Return a P9 rarefaction curve for species."""

    def fig1_reference_comparisons(self):
        """Return P9 figures comparing metasub to skin and soil."""

    def fig1_fraction_unclassified(self):
        """Return a figure showing the fraction of reads which could not be classified."""

    def fig2(self):
        """Figure showing the variation between metasub samples."""
        return [
            self.fig2_umap(),
            self.fig2_pca_flows(),
            self.fig2_region_blocks(),
        ]

    def fig2_umap(self):
        """Return a scatter plot showing a UMAP dimensionality reduction of the data."""
        taxa_umap = umap(self.wide_taxa > 0, n_neighbors=100)
        taxa_umap['continent'] = self.meta['continent']
        taxa_umap['climate'] = self.meta['city_koppen_climate']
        taxa_umap['lat'] = self.meta['latitude']
        taxa_umap['lon'] = self.meta['longitude']
        plot = (
            ggplot(taxa_umap, aes(x='C0', y='C1', color='continent')) +
                geom_point(size=5.5, colour="black") +
                geom_point(size=4) +
                theme_minimal() +
                scale_color_brewer(palette="Set1", direction=1) +
                guides(color = guide_legend(override.aes=list(size=16))) +
                theme_minimal() +
                coord_flip() +
                theme(
                    text = element_text(size=50),
                    panel_grid_major = element_blank(),
                    panel_grid_minor = element_blank(),
                    legend_position='none',
                    axis_text_x=element_blank(),
                    axis_title_x=element_blank(),
                    axis_text_y=element_blank(),
                    axis_title_y=element_blank(),
                    panel_border=element_rect(colour="black", fill='none', size=2),
                )
        )
        return plot

    def fig2_region_blocks(self):
        """Return three panels showing taxa, function, and amr for all samples."""
        phyla = group_small_cols(self.wide_phyla_rel, top=4)
        sample_order = phyla.index[leaves_list(
            linkage(
                squareform(self.tabler.beta_diversity(phyla, metric='jensenshannon')),
                'average'
            )
        )]
        phyla['sample'] = phyla.index
        phyla['continent'] = self.meta['continent']
        phyla = phyla.melt(id_vars=['sample', 'continent'])
        phyla = phyla.dropna()

        amrs = group_small_cols(self.amrs, top=5)
        amrs['sample'] = amrs.index
        amrs['continent'] = self.meta['continent']
        amrs = amrs.melt(id_vars=['sample', 'continent'])
        amrs = amrs.dropna()

        def my_plot(tbl, label):
            return (
                ggplot(tbl, aes(x='sample', y='value', fill='variable', group='continent')) +
                    geom_col() +
                    facet_grid('.~continent', scales="free") +
                    scale_fill_brewer(palette="Set3", direction=1) +
                    guides(color=guide_legend(override_aes=list(size=16))) +
                    theme_minimal() +
                    scale_y_sqrt(expand=c(0, 0)) +
                    labs(fill=label) +
                    theme(
                        text=element_text(size=70),
                        panel_grid_major=element_blank(),
                        panel_grid_minor=element_blank(),
                        legend_position='bottom',
                        axis_text_x=element_blank(),
                        axis_title_x=element_blank(),
                        axis_text_y=element_blank(),
                        axis_title_y=element_blank(),
                        panel_border=element_rect(colour="black", fill=NA, size=2),
                    )
            )

        return [
            my_plot(phyla, 'Phyla'),
            my_plot(self.function_groups, 'Pathways'),
            my_plot(amrs, 'AMR Class'),
        ]

    def fig2_pca_flows(self, n_pcs=100):
        pca = PCA(n_components=n_pcs)
        pcs = pca.fit_transform(self.wide_taxa_rel)
        pcs = pd.DataFrame(data=pcs, index=taxa.index, columns=[f'PC{i}' for i in range(NPCS)])
        pcs['surface'] = self.meta['surface_ontology_fine']
        pcs['temperature'] = core_tabler.metadata['city_ave_june_temp_c']
        pcs['pop_density'] = core_tabler.metadata['city_population_density']
        pcs['continent'] = core_tabler.metadata['continent']
        pcs['city_koppen_climate'] = core_tabler.metadata['city_koppen_climate']
        pcs['sample'] = pcs.index
        pcs = pcs.loc[pcs['surface'] != 'nan']
        pcs = pcs.loc[pcs['surface'] != 'control']
        pcs = pcs.loc[pcs['continent'] != '0']
        var_pcs = pcs.melt(id_vars=['surface', 'sample', 'temperature', 'pop_density', 'continent', 'city_koppen_climate'])

        def scaleit(tbl, covar):
            tbl = tbl.groupby(covar).mean()
            return tbl

        def variance_bars(covar):
            var_bars = var_pcs.groupby('variable').apply(lambda tbl: scaleit(tbl, covar))
            var_bars['variable'] = [int(str(el[0]).split('PC')[1]) for el in var_bars.index]
            var_bars[covar] = [str(el[1]) for el in var_bars.index]
            return var_bars

        def my_plot(covar, label):
            bars = variance_bars(covar)
            return (
                ggplot(bars, aes(x='variable', y='value', fill=covar)) +
                    geom_bar(stat='identity') +
                    theme_minimal() +
                    scale_fill_brewer(palette='Set2') +
                    xlab('Principal Components') +
                    ylab('Mean Value of Covariate') +
                    labs(fill=label) +
                    xlim(0, 25) +
                    ylim(-0.3, 0.5) +
                    ggtitle(label) +
                    theme(
                        text = element_text(size=50),
                        panel_grid_minor=element_blank(),
                        legend_position='right',
                    )
            )

        return [
            my_plot('city_koppen_climate', 'Climate'),
            my_plot('continent', 'Region'),
            my_plot('surface', 'Surface'),
        ]

    def fig5_amrs(self):
        """Figure showing the major AMRs found by MetaSUB."""
        return [
            self.fig5_amr_cooccur(),
            self.fig5_amr_richness_by_city(),
            self.fig5_amr_rarefaction(),
            self.fig5_amr_tree(),
        ]

    def fig5_amr_cooccur(self):
        """Return a heatmap showing co-occurence between AMR genes."""

    def fig5_amr_richness_by_city(self):
        """Return a figure showing the distribution of the number of AMR genes by city."""

    def fig5_amr_rarefaction(self):
        """Return a P9 rarefaction curve for amr genes."""

    def fig5_amr_tree(self):
        """Return an ETE tree showing major AMR types with relative abundances by region."""






















