"""CLI for commands to be related to wasabi."""

import click
import pandas as pd
from json import dumps, loads
from metasub_utils.wasabi.public_files import nonhuman_reads
from metasub_utils.metadata import get_complete_metadata
from capalyzer.packet_parser.normalize import proportions

from .knex import Knex


@click.group()
def pangea():
    pass


def s3uri(url):
    return {
        '__type__': 's3',
        'endpoint_url': 'https://s3.wasabisys.com',
        'uri': url,
    }


def floatif(val):
    try:
        return float(val)
    except ValueError:
        return val


@pangea.command('create-samples')
@click.option('-c', '--city-name', default=None)
@click.option('-t', '--taxa-table', default=None)
@click.argument('username')
@click.argument('password')
def cli_create_samples(city_name, taxa_table, username, password):
    """List unassembled data in the wasabi bucket."""
    knex = Knex().login(username, password)
    metadata = get_complete_metadata()
    if taxa_table:
        taxa_table = proportions(pd.read_csv(taxa_table, index_col=0))
    for sample_name, reads in nonhuman_reads(city_name=city_name).items():
        click.echo(sample_name, err=True)
        sample_metadata = loads(dumps({
            k: floatif(v)
            for k, v in metadata.loc[sample_name].to_dict().items()
            if str(v).lower() != 'nan'
        }))
        sample = knex.add_sample(sample_name, metadata=sample_metadata)
        result = knex.add_sample_result(sample['uuid'], 'nonhuman_reads')
        knex.add_sample_result_field(result['uuid'], 'read_1', s3uri(reads[0]))
        knex.add_sample_result_field(result['uuid'], 'read_2', s3uri(reads[1]))
        if taxa_table is not None:
            taxa_result = knex.add_sample_result(sample['uuid'], 'krakenuniq_taxonomy')
            taxa = taxa_table.loc[sample_name]
            taxa = {k: v for k, v in taxa.to_dict().items() if v > 0}
            knex.add_sample_result_field(taxa_result['uuid'], 'relative_abundance', taxa)
