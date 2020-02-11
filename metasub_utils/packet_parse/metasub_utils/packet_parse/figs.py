import pandas as pd
import networkx as nx
import warnings
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches
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
from plotnine import *
from scipy.cluster.hierarchy import fcluster
from matplotlib import pyplot as plt

from capalyzer.constants import MICROBE_DIR

from .figs_data import MetaSUBFiguresData


class MetaSUBFigures(MetaSUBFiguresData):

    def tbl1(self):
        """Return a pandas dataframe listing where and when samples were collected."""
        tbl = self.meta.copy()

        tbl = tbl.loc[tbl['control_type'].isna()]
        tbl = tbl.loc[~tbl['city'].isna()]
        tbl = tbl.query('city != "other"')
        tbl = pd.crosstab(tbl['city'], tbl['project'])

        tbl['Region'] = self.meta.groupby('city').apply(lambda x: x['continent'].iloc[0])
        tbl['Region'] = tbl['Region'].str.replace('_', ' ').str.title()
        tbl.index = tbl.index.str.replace('_', ' ').str.title()

        tbl = tbl.set_index('Region', append=True)
        tbl = tbl.reorder_levels(['Region', 'city'])
        tbl = tbl.sort_index()

        other_projs = list(tbl.columns[tbl.sum(axis=0) < 100]) + ['PATHOMAP_WINTER']
        tbl['Other'] = tbl[other_projs].sum(axis=1)
        tbl = tbl.drop(columns=other_projs)
        tbl['Total'] = tbl.sum(axis=1)
        tbl = tbl[['PILOT', 'CSD16', 'CSD17', 'Other', 'Total']]  # column order

        continent_totals = tbl.groupby(level=0).sum()
        continent_totals['city'] = 'AAA Region Total'  # AAA so sort puts these first
        continent_totals = continent_totals.set_index('city', append=True)
        tbl = pd.concat([tbl, continent_totals]).sort_index()

        ctrl = self.meta.copy()
        ctrl = ctrl.loc[~ctrl['control_type'].isna()]
        ctrl = pd.crosstab(ctrl['control_type'], ctrl['project'])

        ctrl.index.names = ['city']
        ctrl['Region'] = 'Control'
        ctrl = ctrl.set_index('Region', append=True)
        ctrl = ctrl.reorder_levels(['Region', 'city'])

        other_projs = ctrl.columns[ctrl.sum(axis=0) < 10]
        ctrl['Other'] = ctrl[other_projs].sum(axis=1)
        ctrl = ctrl.drop(columns=other_projs)
        ctrl['Total'] = ctrl.sum(axis=1)
        cols = [
            col for col in ['PILOT', 'CSD16', 'CSD17', 'Other', 'Total']
            if col in ctrl.columns
        ]
        ctrl = ctrl[cols]

        tbl = pd.concat([ctrl, tbl])
        tbl.index = tbl.index.set_levels(tbl.index.levels[1].str.replace('AAA', ''), level=1)

        return tbl

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
                scale_color_brewer(type='qualitative', palette=6, direction=1) +
                scale_fill_brewer(type='qualitative', palette=6, direction=1) +
                theme(
                    text=element_text(size=20),
                    axis_text_x=element_text(angle=0, hjust=1),
                    figure_size=(8, 8),
                    legend_position='none',
                )
        )
        return plot

    def fig1_major_taxa_curves(self, N=75):
        """Return two P9 panels showing prevalence and abundance distributions of major taxa."""
        taxa = self.wide_taxa_rel
        city = taxa.groupby(by=self.meta['city']).median()

        top_taxa = taxa.mean().sort_values(ascending=False)[:N].index
        taxa, city = 1000 * 1000 * taxa[top_taxa], 1000 * 1000 * city[top_taxa]
        taxa_prev, city_prev = prevalence(taxa), prevalence(city)
        taxa_prev = pd.DataFrame({'taxon': taxa_prev.index, 'prevalence': taxa_prev, 'names': taxa_prev.index})
        city_prev = pd.DataFrame({'taxon': city_prev.index, 'prevalence': city_prev, 'names': city_prev.index})
        taxa_mean, taxa_kurtosis, taxa_sd = taxa.mean(), taxa.kurtosis(), taxa.std()

        def add_stats(taxon):
            m, k, sd = taxa_mean[taxon], taxa_kurtosis[taxon], taxa_sd[taxon]
            return f'{taxon} ({m // 1000:.0f}k, {sd // 1000:.0f}k, {k:.0f})'

        taxa.columns = taxa.columns.to_series().apply(add_stats)
        city.columns = city.columns.to_series().apply(add_stats)
        top_taxa_stat = top_taxa.to_series().apply(add_stats)

        taxa, city = taxa.melt(), city.melt()
        taxa['variable'] = pd.Categorical(taxa['variable'], categories=top_taxa_stat)
        city['variable'] = pd.Categorical(city['variable'], categories=top_taxa_stat)
        taxa['kind'] = 'All Samples'
        city['kind'] = 'City Median'
        both = pd.concat([taxa, city])
        abund = (
            ggplot(both, aes(x='value', color='kind')) +
                geom_density(size=1) +
                facet_grid('variable~.', scales="free_y") +
                theme_minimal() +
                ylab('Density') +
                xlab('Abundance (PPM)') +
                scale_x_log10() +
                scale_color_brewer(type='qualitative', palette=6, direction=1) +
                labs(fill="") +
                theme(
                    axis_text_x=element_text(angle=0, hjust=1),
                    strip_text_y=element_text(angle=0, hjust=0),
                    text=element_text(size=20),
                    panel_grid_major_x=element_line(colour="grey", size=0.75),
                    panel_grid_major_y=element_blank(),
                    panel_grid_minor=element_blank(),
                    legend_position='none',
                    axis_title_y=element_blank(),
                    axis_text_y=element_blank(),
                    figure_size=(4, 40),
                )
        )
        taxa_prev['kind'] = 'All Samples'
        city_prev['kind'] = 'City Median'
        taxa_prev['taxon'] = pd.Categorical(taxa_prev['taxon'], categories=top_taxa)
        city_prev['taxon'] = pd.Categorical(city_prev['taxon'], categories=top_taxa)
        both_prev = pd.concat([taxa_prev, city_prev])
        prev = (
            ggplot(both_prev, aes(x='kind', y='prevalence', fill='kind')) +
                geom_col() +
                facet_grid('taxon~.', scales="free_y") +
                theme_minimal() +
                ylab('Prevalence') +
                scale_fill_brewer(type='qualitative', palette=6, direction=1) +
                labs(color="") +
                coord_flip() +
                scale_y_continuous(breaks=(0.1, 0.5, 1)) +
                theme(
                    axis_text_x=element_text(angle=0, hjust=1),
                    axis_text_y=element_blank(),
                    axis_title_y=element_blank(),
                    strip_text_y=element_blank(),
                    text=element_text(size=20),
                    panel_grid_major=element_blank(),
                    legend_position='left',
                    figure_size=(2, 40),
                )
        )
        return abund, prev

    def fig1_species_rarefaction(self, w=100):
        """Return a P9 rarefaction curve for species."""
        ns = range(w, self.wide_taxa.shape[0], w)
        rare = rarefaction_analysis(self.wide_taxa, ns=ns)
        return (
            ggplot(rare, aes(x='N', y='Taxa')) +
                geom_point(size=4, colour="black") +
                geom_smooth(color='blue') +
                theme_minimal() +
                theme(
                    text=element_text(size=20),
                    figure_size=(8, 8),
                )
        )

    def fig1_reference_comparisons(self):
        """Return P9 figures comparing metasub to skin and soil."""

        def my_plot(tbl, y_lab, yint, yint_lab):
            return (
                ggplot(tbl, aes(x='continent', y='jaccard', fill='continent')) +
                    geom_violin(width=1.2) +
                    geom_boxplot(fill='white', width=0.1) +
                    theme_minimal() +
                    scale_y_sqrt() +
                    ylim(0, 0.5) +
                    scale_fill_brewer(type='qualitative', palette=6, direction=1) +
                    xlab('') +
                    ylab(y_lab) +
                    geom_hline(yintercept=yint, color='red', size=4) +
                    annotate(geom='label', x='Oceania', y=(yint - 0.015), label=yint_lab, size=20) +
                    theme(
                        text=element_text(size=20),
                        figure_size=(8, 8),
                        legend_position='none',
                        axis_text_x=element_text(angle=90),
                    )
            )

        return [
            my_plot(self.emp, 'MASH Jaccard Distance to Soil', 0.16451445767195777, "Soil-Soil Mean"),
            my_plot(
                self.hmp.query('body_site == "skin"'), 'MASH Jaccard Distance to Skin',
                0.083, "Skin-Skin Mean"
            ),
        ]

    def fig1_fraction_unclassified(self):
        """Return a figure showing the fraction of reads which could not be classified."""
        return (
            ggplot(self.rps, aes(x='continent', y='unknown', fill='continent')) +
                geom_violin() +
                geom_boxplot(fill='white', width=0.1) +
                theme_minimal() +
                scale_fill_brewer(type='qualitative', palette=6, direction=1) +
                xlab('Region') +
                ylab('Fraction Unclassified DNA') +
                theme(
                    text=element_text(size=20),
                    axis_text_x=element_text(hjust=1, angle=30),
                    figure_size=(8, 8),
                    legend_position='none',
                )
        )

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
                scale_color_brewer(type='qualitative', palette=3, direction=1) +
                theme_minimal() +
                coord_flip() +
                theme(
                    text=element_text(size=50),
                    panel_grid_major=element_blank(),
                    panel_grid_minor=element_blank(),
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
                    scale_color_brewer(type='qualitative', palette=3, direction=1) +
                    theme_minimal() +
                    scale_y_sqrt(expand=(0, 0)) +
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
                        panel_border=element_rect(colour="black", size=2),
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
        pcs = pd.DataFrame(
            data=pcs,
            index=self.wide_taxa_rel.index,
            columns=[f'PC{i}' for i in range(n_pcs)]
        )
        pcs['surface'] = self.meta['surface_ontology_fine']
        pcs['temperature'] = self.meta['city_ave_june_temp_c']
        pcs['pop_density'] = self.meta['city_population_density']
        pcs['continent'] = self.meta['continent']
        pcs['city_koppen_climate'] = self.meta['city_koppen_climate']
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
                        text=element_text(size=50),
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
        tbl = self.amrs > 0
        amr_jaccard = 1 - pd.DataFrame(
            squareform(pdist(tbl, metric='jaccard')),
            index=tbl.index, columns=tbl.index
        )

        AMR_CLASSES = set(self.amrs.columns)

        def get_amr_class(el):
            for amr_class in AMR_CLASSES:
                if amr_class in el:
                    return amr_class
            return 'unknown'

        amr_class = amr_jaccard.index.map(get_amr_class)
        lut = dict(zip(amr_class.unique(), sns.hls_palette(amr_class.nunique())))
        lut['unknown'] = (0.9, 0.9, 0.9)
        class_colors = amr_class.map(lut)

        return sns.clustermap(
            amr_jaccard, center=0.35, cmap="RdBu_r",
            row_colors=class_colors,
            figsize=(40, 40)
        )

    def fig5_amr_richness_by_city(self):
        """Return a figure showing the distribution of the number of AMR genes by city."""
        richness_city = (self.amrs + 0.000000001).apply(richness, axis=1)
        richness_city = pd.concat([self.meta['city'], self.meta['continent'], richness_city], axis=1)
        richness_city.columns = ['city', 'continent', 'richness']
        richness_city = richness_city.dropna()

        cities = richness_city['city'].value_counts()
        richness_city = richness_city.loc[richness_city['city'].isin(cities[cities > 3].index)]
        richness_city = richness_city.groupby('city').filter(lambda tbl: sum(tbl['richness'] > 0) >= 3)

        return (
            ggplot(richness_city, aes(x='richness', fill='continent')) +
                geom_density(size=0.5) +
                facet_grid('city~.', scales="free_y") +
                theme_minimal() +
                ylab('Density') +
                xlab('Number of AMRs Detected') +
                scale_x_log10() +
                scale_fill_brewer(type='qualitative', palette=3, direction=1) +
                labs(fill="Region") +
                theme(
                    axis_text_x=element_text(angle=0, hjust=1),
                    axis_text_y=element_blank(),
                    strip_text_y=element_text(angle=0, hjust=0),
                    text=element_text(size=20),
                    panel_grid_major=element_blank(),
                    panel_grid_minor=element_blank(),
                    legend_position='bottom'
                )
        )

    def fig5_amr_rarefaction(self):
        """Return a P9 rarefaction curve for amr genes."""
        ns = range(1, self.amrs.shape[0], 10)
        rare = rarefaction_analysis(self.amrs, ns=ns)
        return (
            ggplot(rare, aes(x='N', y='Taxa')) +
                geom_point(size=4, colour="black") +
                geom_smooth() +
                theme_minimal() +
                theme(
                    text=element_text(size=50),
                )
        )

    def fig5_amr_tree(self):
        """Return an ETE tree showing major AMR types with relative abundances by region."""






















