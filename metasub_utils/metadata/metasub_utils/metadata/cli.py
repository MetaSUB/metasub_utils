"""CLI for commands metadata commands."""

import click

from .metadata import (
    get_canonical_city_names,
    get_complete_metadata,
    get_samples_from_city,
)


@click.group()
def metadata():
    pass


@metadata.command('cities')
def cli_get_canonical_city_names():
    """Print a list of canonical city names."""
    for city_name in get_canonical_city_names():
        print(city_name)


@metadata.command('metadata')
@click.option('--uploadable/--complete', default=False, help='optimize table for metagenscope')
def cli_get_metadata(uploadable):
    """Print a CSV with MetaSUB metadata."""
    tbl = get_complete_metadata(uploadable=uploadable)
    print(tbl.to_csv())


@metadata.command('samples-from-city')
@click.argument('city_name')
def cli_get_samples_from_city(city_name):
    """Print the names of samples from the specified city."""
    sample_names = get_samples_from_city(city_name)
    for sample_name in sample_names:
        click.echo(sample_name)
