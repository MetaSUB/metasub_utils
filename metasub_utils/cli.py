# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click
from sys import (
    stderr,
    exit,
)
from .constants import ATHENA
from .metagenscope import upload_cities
from .utils import (
    get_complete_metadata,
    get_canonical_city_names,
    as_display_name,
)


@click.group()
def main(args=None):
    """Console script for metasub_utils."""
    pass


###############################################################################


@main.group()
def get():
    pass


@get.command('cities')
def cli_get_canonical_city_names():
    """Print a list of canonical city names."""
    for city_name in get_canonical_city_names():
        print(city_name)


@get.command('metadata')
@click.option('--uploadable/--complete', default=False, help='optimize table for metagenscope')
def cli_get_metadata(uploadable):
    """Print a CSV with MetaSUB metadata."""
    tbl = get_complete_metadata(uploadable=uploadable)
    print(tbl.to_csv())


###############################################################################


@main.group()
def upload():
    pass


@upload.command(name='city')
@click.option('--dryrun/--wetrun', default=True)
@click.option('--upload-only/--run-middleware', default=False)
@click.option('-n', '--display-name', default=None)
@click.argument('city_names', nargs=-1)
def cli_upload_city(dryrun, upload_only, display_name, city_names):
    result_dir = ATHENA.METASUB_RESULTS
    if len(city_names) == 1 and display_name is None:
        display_name = as_display_name(city_names[0])
    elif len(city_names) > 1 and display_name is None:
        print('Display name cannot be blank if multiple cities are listed', file=stderr)
        exit(1)
    upload_cities(
        result_dir, city_names, display_name,
        upload_only=upload_only,
        dryrun=dryrun
    )


###############################################################################


if __name__ == "__main__":
    main()
