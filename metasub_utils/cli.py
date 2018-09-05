# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click
from sys import (
    stderr,
    exit,
)
from .constants import ATHENA, BRIDGES
from .metagenscope import upload_cities
from .utils import (
    get_complete_metadata,
    get_canonical_city_names,
    as_display_name,
)
from .hudson_alpha import (
    process_flowcells,
    rename_sl_names_to_ha_unique,
    map_from_name_in_datasuper_to_ha_unique,
    rename_existing_core_results,
)
from .assemblies import (
    upload_metaspades_assemblies_from_bridges,
    copy_metaspades_assemblies_from_bridges,
)
from .wasabi_bucket import WasabiBucket


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
def wasabi():
    pass


@wasabi.command('list')
@click.argument('profile_name', default='wasabi')
def cli_list_wasabi_files(profile_name):
    """List all files in the wasabi bucket."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    for file_key in wasabi_bucket.list_files():
        print(file_key)


@wasabi.command('download-contigs')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('target_dir', default='assemblies')
def cli_download_contig_files(dryrun, profile_name, target_dir):
    """Download contig files from wasabi."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.download_contigs(
        target_dir=target_dir,
        dryrun=dryrun,
    )


@wasabi.command('upload-results')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('result_dir', default=ATHENA.METASUB_RESULTS)
def cli_upload_results(dryrun, profile_name, result_dir):
    """Upload CAP results to wasabi. Only works on Athena."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.upload_results(
        result_dir=result_dir,
        dryrun=dryrun,
    )


@wasabi.command('upload-contigs')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('result_dir', default=BRIDGES.ASSEMBLIES)
def cli_upload_contigs(dryrun, profile_name, result_dir):
    """Upload CAP results to wasabi. Only works on bridges."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.upload_contigs(
        result_dir=result_dir,
        dryrun=dryrun,
    )


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
    """Upload a city to MetaGenScope. Only works on Athena."""
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


@upload.command(name='assemblies')
@click.option('--dryrun/--wetrun', default=True)
@click.argument('username')
@click.argument('password')
def cli_upload_assemblies(dryrun, username, password):
    """Upload assemblies from bridges to Zurich SFTP"""
    upload_metaspades_assemblies_from_bridges(username, password, dryrun=dryrun)


###############################################################################


@main.group()
def copy():
    pass


@copy.command(name='assemblies')
@click.argument('target_dir')
def cli_copy_assemblies(target_dir):
    """Copy assemblies to a new dir on bridges."""
    copy_metaspades_assemblies_from_bridges(target_dir)

###############################################################################


@main.group()
def download():
    pass


@download.command(name='ha')
@click.option('--dryrun/--wetrun', default=True)
@click.argument('username')
@click.argument('password')
def cli_download_ha_files(dryrun, username, password):
    """Download flowcells from Hudson Alpha, intended for Athena."""
    process_flowcells(dryrun, (username, password))


###############################################################################


@main.group()
def athena():
    pass


@athena.command(name='rename-sl-files')
def cli_rename_sl_files():
    """Print a two column file of old path to new path."""
    rename_sl_names_to_ha_unique()


@athena.command(name='datasuper-to-hauniq')
@click.argument('source_fastqs', type=click.File('r'))
def cli_datasuper_to_hauniq(source_fastqs):
    """Print a two column file of datasuper name to ha uniq."""
    for ds_name, ha_uniq in map_from_name_in_datasuper_to_ha_unique(source_fastqs).items():
        print(f'{ds_name} {ha_uniq}')


@athena.command(name='new-core-results')
@click.argument('source_fastqs', type=click.File('r'))
@click.argument('old_result_dir')
def cli_new_core_results(source_fastqs, old_result_dir):
    """Print a two column file of old result path to result path with ha uniq."""
    for ds_name, ha_uniq in rename_existing_core_results(source_fastqs, old_result_dir).items():
        print(f'{ds_name} {ha_uniq}')


###############################################################################


if __name__ == "__main__":
    main()
