"""Utilities for working with assemblies and bridges."""

from glob import glob
from os.path import dirname

from .constants import *


def hauid_from_metaspades_dir(contig_path, sl_tbl):
    tkns = contig_path.split('haib')[1].split('/')
    haib = 'haib' + tkns[0]
    flowcell = tkns[1]
    raw_id = tkns[2].split('_1.fastq.gz.metaspades')[0].split('.R1.fastq.gz.metaspades')[0]
    sl_id = sl_tbl[raw_id].split('_')[2]
    return haib, flowcell, sl_id


def get_bridges_metaspades_dirs():
    contig_files = glob(METASUB_DATA + '/**/contigs.fasta', recursive=True)
    metaspades_dirs = {
        dirname(contig_file)
        for contig_file in contig_files
    }
    return metaspades_dirs


def parse_sl_table():
    tbl = {}
    with open(SL_TABLE) as sl_file:
        for line in sl_file:
            line = line.strip()
            if not line:
                continue
            tkns = line.split()
            tbl[tkns[0]] = tkns[1]
    return tbl
