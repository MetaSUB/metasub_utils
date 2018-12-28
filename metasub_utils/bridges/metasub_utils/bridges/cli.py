"""CLI for commands to be run on bridges."""

import click

from metasub_utils.wasabi import WasabiBucket

from .bridges import (
    upload_metaspades_assemblies_from_bridges,
    copy_metaspades_assemblies_from_bridges
)
from .constants import *


@click.group()
def bridges():
    pass


@bridges.command(name='upload-assemblies-to-zurich')
@click.option('--dryrun/--wetrun', default=True)
@click.argument('username')
@click.argument('password')
def cli_upload_assemblies(dryrun, username, password):
    """Upload assemblies from bridges to Zurich SFTP"""
    upload_metaspades_assemblies_from_bridges(username, password, dryrun=dryrun)


@bridges.command('upload-contigs')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.option('-p', '--profile-name', default='wasabi')
@click.argument('result_dir', default=ASSEMBLIES)
def cli_upload_contigs(dryrun, profile_name, result_dir):
    """Upload CAP results to wasabi. Only works on bridges."""
    wasabi_bucket = WasabiBucket(profile_name=profile_name)
    wasabi_bucket.upload_contigs(
        result_dir=result_dir,
        dryrun=dryrun,
    )
    wasabi_bucket.close()


@bridges.command(name='copy-assemblies')
@click.argument('target_dir')
def cli_copy_assemblies(target_dir):
    """Copy assemblies to a new dir on bridges."""
    copy_metaspades_assemblies_from_bridges(target_dir)
