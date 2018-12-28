
import click

from metasub_utils.data_packet.filter_data_packet import (
    make_city_packet,
    make_sub_packet,
)


@click.group()
def main():
    pass


@main.command('generic-sub-packet')
@click.option('-p', '--packet-dir', default='.')
@click.argument('sample_names')
@click.argument('sub_packet_dir')
def cli_make_generic_sub_packet(packet_dir, sample_names, sub_packet_dir):
    """Make tables for a sub packet given a list of sample names."""
    make_sub_packet(sub_packet_dir, sample_names, data_packet_dir=packet_dir)


@main.command('city-sub-packet')
@click.option('-p', '--packet-dir', default='.')
@click.argument('city_name')
def cli_make_city_packet(packet_dir, city_name):
    """Make a data packet with only samples from the specified city."""
    make_city_packet(city_name, data_packet_dir=packet_dir)


if __name__ == '__main__':
    main()
