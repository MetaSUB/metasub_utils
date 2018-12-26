
from glob import glob
from subprocess import call
from os import makedirs
from os.path import join, basename

from metasub_utils.metadata import get_complete_metadata


def filter_file(source_file, sample_names_filename, out_filename):
    cmd = (
        f'cat {source_file} | head -1 > {out_filename} && '
        f'cat {source_file} | grep -Ff {sample_names_filename} >> {out_filename}'
    )
    call(cmd, shell=True)


def get_samples_in_city(city_name):
    metadata = get_complete_metadata()
    return metadata[metadata['city'] == city_name].index


def make_city_packet(city_name, data_packet_dir='.'):
    city_name = city_name.lower()
    city_packet_dir = join(data_packet_dir, f'city_packets/{city_name}')
    makedirs(city_packet_dir, exist_ok=True)

    sample_names = get_samples_in_city(city_name)
    sample_names_filename = join(city_packet_dir, f'{city_name}_sample_names.txt')
    with open(sample_names_filename, 'w') as snf:
        for sample_name in sample_names:
            print(sample_name, file=snf)

    for packet_sub_dir in ['antimicrobial_resistance', 'metadata', 'other', 'taxonomy']:
        city_packet_sub_dir = join(city_packet_dir, packet_sub_dir)
        makedirs(city_packet_sub_dir, exist_ok=True)
        packet_sub_dir = join(data_packet_dir, packet_sub_dir)
        tables = glob(packet_sub_dir + '/*.csv')
        for table in tables:
            city_table_filename = join(city_packet_sub_dir, basename(table))
            filter_file(table, sample_names_filename, city_table_filename)
