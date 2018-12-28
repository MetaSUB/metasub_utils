"""CLI for commands to be run on bridges."""

import click

from sys import stderr

from metasub_utils.athena.constants import METASUB_RESULTS


@click.group()
def mgs():
    pass


@mgs.command(name='upload-city')
@click.option('--dryrun/--wetrun', default=True)
@click.option('--upload-only/--run-middleware', default=False)
@click.option('-n', '--display-name', default=None)
@click.option('--display-name-suffix', default=None)
@click.argument('city_names', nargs=-1)
def cli_upload_city(dryrun, upload_only, display_name, display_name_suffix, city_names):
    """Upload a city to MetaGenScope. Only works on Athena."""
    result_dir = METASUB_RESULTS
    if len(city_names) == 1 and display_name is None:
        display_name = as_display_name(city_names[0])
    elif len(city_names) > 1 and display_name is None:
        print('Display name cannot be blank if multiple cities are listed', file=stderr)
        exit(1)
    if display_name_suffix:
        display_name += display_name_suffix
    upload_cities(
        result_dir, city_names, display_name,
        upload_only=upload_only,
        dryrun=dryrun
    )
