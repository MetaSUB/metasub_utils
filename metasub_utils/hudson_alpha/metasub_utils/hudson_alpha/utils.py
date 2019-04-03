"""Utilities for Hudson Alpha."""

import requests
from os.path import basename

from .constants import *


def download_file(url, path, auth):
    """Download a file."""
    r = requests.get(url, auth=auth)
    open(path, 'wb').write(r.content)


def parse_flowcell_table():
    """Return a list representing all the flowcells in hudson_alpha_flowcells.csv."""
    with open(FLOWCELL_FILENAME) as flowcell_file:
        flowcells = [line.strip().split(',') for line in flowcell_file if len(line.strip()) > 0]
    return flowcells


def get_root_and_read_number(filepath):
    """For a paired fastq file return the root of the file and the read number."""
    filename = basename(filepath)
    if '_1.' in filename:
        return filename.split('_1.')[0], '1'
    elif '.R1.' in filename:
        return filename.split('.R1.')[0], '1'
    elif '_2.' in filename:
        return filename.split('_2.')[0], '2'
    elif '.R2.' in filename:
        return filename.split('.R2.')[0], '2'
    assert False, filepath


def parse_ha_filename_file(ha_filename_path):
    """Return a parsed ha_filenames file as a dict."""
    name_map = {}
    with open(ha_filename_path) as hfp:
        hfp.readline()
        hfp.readline()
        for line in hfp:
            line = line.strip()
            if not line:
                continue
            tkns = line.split('\t')
            try:
                slname, trip_name, = tkns[2], tkns[3]
            except IndexError:
                continue
            if len(tkns) >= 6:
                description_name = tkns[5].split()[0]
                name_map[description_name] = slname
            name_map[slname] = slname
            name_map[trip_name] = slname
    return name_map
