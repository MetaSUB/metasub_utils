
import click
import pandas as pd
from os.path import join

from metasub_utils.data_packet.filter_data_packet import (
    make_city_packet,
    make_sub_packet,
)

from .clean_metadata import clean_metadata_table


@click.group()
def packet():
    pass


@packet.command('generic-sub-packet')
@click.option('-p', '--packet-dir', default='.')
@click.argument('sample_names')
@click.argument('sub_packet_dir')
def cli_make_generic_sub_packet(packet_dir, sample_names, sub_packet_dir):
    """Make tables for a sub packet given a list of sample names."""
    make_sub_packet(sub_packet_dir, sample_names, data_packet_dir=packet_dir)


@packet.command('city-sub-packet')
@click.option('-p', '--packet-dir', default='.')
@click.argument('city_name')
def cli_make_city_packet(packet_dir, city_name):
    """Make a data packet with only samples from the specified city."""
    make_city_packet(city_name, data_packet_dir=packet_dir)


@packet.command('release-metadata')
@click.argument('raw_metadata', type=click.File('r'))
def cli_make_release_metadata(raw_metadata):
    """Make a data packet suitable for release."""
    raw_meta = pd.read_csv(raw_metadata, dtype=str)
    meta, cntrl_meta, dupe_meta, dupe_map = clean_metadata_table(raw_meta)

    meta.to_csv('release_metadata.csv')
    cntrl_meta.to_csv('control_metadata.csv')
    dupe_meta.to_csv('duplicate_metadata.csv')
    dupe_map.to_csv('duplicate_map.csv')


@packet.command('release-packet')
@click.argument('raw_packet')
@click.argument('raw_metadata', type=click.File('r'))
@click.argument('new_packet')
def cli_make_release_packet(raw_packet, raw_metadata, new_packet):
    """Make a data packet suitable for release."""
    raw_meta = pd.read_csv(raw_metadata, dtype=str)
    meta, cntrl_meta, dupe_meta, dupe_map = clean_metadata_table(raw_meta)
    make_sub_packet(new_packet, meta['uuid'], data_packet_dir=raw_packet, copy_metadata=False)
    meta.to_csv(join(new_packet, 'metadata', 'complete_metadata.csv'))
    click.echo('Built main packet', err=True)

    cntrl_packet = join(new_packet, 'controls')
    make_sub_packet(cntrl_packet, cntrl_meta['uuid'], data_packet_dir=new_packet, copy_metadata=False)
    cntrl_meta.to_csv(join(cntrl_packet, 'metadata', 'complete_metadata.csv'))
    click.echo('Built control packet', err=True)

    dupe_packet = join(new_packet, 'duplicates')
    all_dupes = set(dupe_map.iloc[:, 0]) | set(dupe_map.iloc[:, 1])
    make_sub_packet(dupe_packet, all_dupes, data_packet_dir=raw_packet, copy_metadata=False)
    dupe_meta.to_csv(join(dupe_packet, 'metadata', 'complete_metadata.csv'))
    dupe_map.to_csv(join(dupe_packet, 'metadata', 'duplicate_map.csv'))
    click.echo('Built duplicate packet', err=True)


if __name__ == '__main__':
    packet()
