"""CLI for hudson alpha related commands."""

import click
from metasub_utils.cli import main


@click.group()
def hudsonalpha():
    pass


main.add_command(hudsonalpha)


@hudsonalpha.command(name='download')
@click.option('--dryrun/--wetrun', default=True)
@click.argument('username')
@click.argument('password')
def cli_download_ha_files(dryrun, username, password):
    """Download flowcells from Hudson Alpha, intended for Athena."""
    process_flowcells(dryrun, (username, password))
