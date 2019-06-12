
from glob import glob
from subprocess import call
from os import makedirs
from os.path import join, basename, isfile
from tempfile import NamedTemporaryFile

from metasub_utils.metadata import get_complete_metadata


def filter_file(source_file, sample_names_filename, out_filename, no_overwrite=True):
    if no_overwrite and isfile(out_filename):
        return
    cmd = (
        f'cat {source_file} | head -1 > {out_filename} && '
        f'cat {source_file} | grep -Ff {sample_names_filename} >> {out_filename}'
    )
    call(cmd, shell=True)


def get_samples_in_city(city_name):
    metadata = get_complete_metadata()
    return metadata[metadata['city'] == city_name].index


def make_city_packet(city_name, data_packet_dir='.'):
    """Make a data packet for a given city."""
    city_name = city_name.lower()
    city_packet_dir = join(data_packet_dir, f'city_packets/{city_name}')
    makedirs(city_packet_dir, exist_ok=True)

    sample_names = get_samples_in_city(city_name)
    sample_names_filename = join(city_packet_dir, f'{city_name}_sample_names.txt')
    with open(sample_names_filename, 'w') as snf:
        for sample_name in sample_names:
            print(sample_name, file=snf)

    make_sub_packet(city_packet_dir, sample_names_filename, data_packet_dir=data_packet_dir)


def make_sub_packet(sub_packet_dir, sample_names_file, data_packet_dir='.', copy_metadata=True):
    """Make a sub packet given a directory and a list of sample names."""

    if isinstance(sample_names_file, str):
        sample_names_filename = sample_names_file
    else:
        with NamedTemporaryFile(mode='w', delete=False) as snf:
            for sample_name in sample_names_file:
                print(sample_name, file=snf)
            sample_names_filename = snf.name

    for packet_sub_dir in ['antimicrobial_resistance', 'metadata', 'other', 'taxonomy', 'pathways']:
        sub_packet_sub_dir = join(sub_packet_dir, packet_sub_dir)
        makedirs(sub_packet_sub_dir, exist_ok=True)
        packet_sub_dir = join(data_packet_dir, packet_sub_dir)
        if packet_sub_dir == 'metadata' and not copy_metadata:
            continue
        tables = glob(packet_sub_dir + '/*.csv')
        for table in tables:
            sub_table_filename = join(sub_packet_sub_dir, basename(table))
            filter_file(table, sample_names_filename, sub_table_filename)
