"""CLI for commands metadata commands."""

import click
from metasub_utils.cli import main


@click.group()
def metadata():
    pass


main.add_command(metadata)


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
