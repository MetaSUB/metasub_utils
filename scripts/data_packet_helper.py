
import click
from glob import glob
from os.path import join, dirname, basename
from subprocess import check_call


def city_packet(sample_filename, long_taxa, wide_taxa, base_taxa):
    print(sample_filename)
    city_packet_dir = dirname(sample_filename)
    # city_long = f'{city_packet_dir}/taxonomy/{basename(long_taxa)}'[:-3]
    # cmd = (
    #     f'gunzip -c {long_taxa} | head -1 > {city_long} '
    #     f'&& gunzip -c {long_taxa} | grep -Ff {sample_filename} >> {city_long} '
    #     f'&& gzip {city_long}'
    # )
    #  check_call(cmd, shell=True)

    # city_wide = f'{city_packet_dir}/taxonomy/{basename(wide_taxa)}'
    # cmd = (
    #     f'cat {wide_taxa} | head -4 > {city_wide} '
    #     f'&& cat {wide_taxa} | grep -Ff {sample_filename} >> {city_wide} '
    # )
    # check_call(cmd, shell=True)

    city_base_taxa = f'{city_packet_dir}/taxonomy/{basename(base_taxa)}'
    cmd = (
        f'cat {base_taxa} | head -4 > {city_base_taxa} '
        f'&& cat {base_taxa} | grep -Ff {sample_filename} >> {city_base_taxa} '
    )
    check_call(cmd, shell=True)


@click.command()
@click.argument('packet_dir')
def main(packet_dir):
    wide_taxa = f'{packet_dir}/taxonomy/refseq.krakenhll_wide.read_counts.csv'
    long_taxa = f'{packet_dir}/taxonomy/refseq.krakenhll_longform.csv.gz'
    base_taxa = f'{packet_dir}/taxonomy/refseq.krakenhll_species.csv'
    sample_filenames = glob(f'{packet_dir}/city_packets/*/*_sample_names.txt')
    for sample_filename in sample_filenames:
        city_packet(sample_filename, long_taxa, wide_taxa, base_taxa)


if __name__ == '__main__':
    main()
