"""CLI for commands to be run on athena."""

import click

from metasub_utils.wasabi import WasabiBucket

from .constants import *


@click.group()
def athena():
    pass


@athena.command('upload-results')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('result_dir', default=METASUB_RESULTS)
def cli_upload_results(dryrun, profile_name, result_dir):
    """Upload CAP results to wasabi. Only works on Athena."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.upload_results(
        result_dir=result_dir,
        dryrun=dryrun,
    )
    wasabi_bucket.close()


@athena.command('upload-data')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('data_dir', default=HALPHA_LIBRARY)
def cli_upload_raw_data(dryrun, profile_name, data_dir):
    """Upload CAP results to wasabi. Only works on Athena."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.upload_raw_data(
        data_dir=data_dir,
        dryrun=dryrun,
    )
    wasabi_bucket.close()


@athena.group()
def migrate():
    pass


@migrate.command(name='rename-sl-files')
def cli_rename_sl_files():
    """Print a two column file of old path to new path."""
    rename_sl_names_to_ha_unique()


@migrate.command(name='datasuper-to-hauniq')
@click.argument('source_fastqs', type=click.File('r'))
def cli_datasuper_to_hauniq(source_fastqs):
    """Print a two column file of datasuper name to ha uniq."""
    for ds_name, ha_uniq in map_from_name_in_datasuper_to_ha_unique(source_fastqs).items():
        print(f'{ds_name} {ha_uniq}')


@migrate.command(name='new-core-results')
@click.argument('source_fastqs', type=click.File('r'))
@click.argument('old_result_dir')
def cli_new_core_results(source_fastqs, old_result_dir):
    """Print a two column file of old result path to result path with ha uniq."""
    for ds_name, ha_uniq in rename_existing_core_results(source_fastqs, old_result_dir).items():
        print(f'{ds_name} {ha_uniq}')
