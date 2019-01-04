"""CLI for commands to be related to wasabi."""

import click

from .wasabi_bucket import WasabiBucket


@click.group()
def wasabi():
    pass


@wasabi.command('list')
@click.argument('profile_name', default='wasabi')
def cli_list_wasabi_files(profile_name):
    """List all files in the wasabi bucket."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    for file_key in wasabi_bucket.list_files():
        print(file_key)


@wasabi.command('list-unassembled')
@click.argument('profile_name', default='wasabi')
def cli_list_unassembled_data(profile_name):
    """List unassembled data in the wasabi bucket."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    for file_key in wasabi_bucket.list_unassembled_data():
        print(file_key)


@wasabi.command('list-raw-reads')
@click.option('-p', '--profile-name', default='wasabi')
@click.option('-c', '--city-name', default=None)
def cli_list_raw_reads(profile_name, city_name):
    """List unassembled data in the wasabi bucket."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    for file_key in wasabi_bucket.list_raw(city_name=city_name):
        print(file_key)


@wasabi.command('download-raw-reads')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.option('-c', '--city-name', default=None)
@click.argument('target_dir', default='data')
def cli_download_raw_data(dryrun, profile_name, city_name, target_dir):
    """Download raw sequencing data, from a particular city if specified."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.download_raw(
        city_name=city_name,
        target_dir=target_dir,
        dryrun=dryrun,
    )
    wasabi_bucket.close()


@wasabi.command('download-unassembled-data')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('target_dir', default='data')
def cli_download_unassembled_data(dryrun, profile_name, target_dir):
    """Download data without contig files from wasabi."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.download_unassembled_data(
        target_dir=target_dir,
        dryrun=dryrun,
    )
    wasabi_bucket.close()


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
    wasabi_bucket.close()
