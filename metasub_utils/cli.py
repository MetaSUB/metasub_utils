# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click
from .constants import ATHENA
from .metagenscope import upload_city


@click.group()
def main(args=None):
    """Console script for metasub_utils."""
    pass


@main.group()
def upload():
    pass


@upload.command(name='city')
@click.option('--upload-only/--run-middleware', default=False)
@click.argument('city_name')
def cli_upload_city(upload_only, city_name):
    result_dir = ATHENA.METASUB_RESULTS
    upload_city(result_dir, city_name, upload_only=upload_only)


if __name__ == "__main__":
    main()
