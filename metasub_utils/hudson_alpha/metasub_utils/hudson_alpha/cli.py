"""CLI for hudson alpha related commands."""

import click

from .hudson_alpha import process_flowcells


@click.group()
def hudsonalpha():
    pass


@hudsonalpha.command(name='download')
@click.option('--dryrun/--wetrun', default=True)
@click.argument('username')
@click.argument('password')
def cli_download_ha_files(dryrun, username, password):
    """Download flowcells from Hudson Alpha, intended for Athena."""
    process_flowcells(dryrun, (username, password))
