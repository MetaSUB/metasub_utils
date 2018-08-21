"""
Procedure for handling data from HA:
1. Each new flowcell url should be recorded in 'hudson_alpha_flowcells.csv'
   along with its metasub_project_name, and H.A. project names
2. A new 'library' directory should be created as <library_top>/<HA project ID>/<flowcell number>
3. The relevant file and filenames files hould be downloaded to this dir
4. All fragmented files should be downloaded to the new dir
5. All fragmented files should be concatenated within the dir and the fragments deleted.
   Each file should now have an 'SL' name
"""

from .constants import HALPHA
from glob import glob
from os.path import join, makedirs, basename, isfile
from urllib.request import urlretrieve


def process_flowcells(dryrun, ha_username, ha_password):
    with open(HALPHA.FLOWCELL_FILENAME) as flowcell_file:
        tkn_gen = (
            line.strip().split(',')
            for line in flowcell_file
            if len(line.strip()) > 0
        )
        for metasub_project_name, _, ha_project_id, ha_file_url in tkn_gen:
            flowcell_number = ha_file_url.split('files_')[-1].split('.txt')[0]
            ha_file_url = HALPHA.URL.format(ha_username, ha_password) + ha_file_url
            ha_filename_url = 'filenames'.join(ha_file_url.split('files'))
            library_dir = join(HALPHA.ATHENA_SL_LIBRARY, ha_project_id, flowcell_number)
            makedirs(library_dir, exist_ok=True)
            ha_file_path = join(library_dir, ha_file_url.split('/')[-1])
            urlretrieve(ha_file_url, ha_file_path)
            ha_filename_path = join(library_dir, ha_filename_url.split('/')[-1])
            urlretrieve(ha_filename_url, ha_filename_path)
            handle_single_flowcell()


def parse_filename(ha_filename_path):
    name_map = {}
    with open(ha_filename_path) as hfp:
        for line in hfp:
            line = line.strip()
            if len(line) == 0:
                continue
            tkns = line.split('\t')
            slname, trip_name, description_name = tkns[2], tkns[3], tkns[5]
            name_map[slname] = slname
            name_map[trip_name] = slname
            name_map[description_name] = slname
    return name_map


def get_root_and_read_number(filepath):
    filename = basename(filepath)
    if '_1' in filename:
        return filename.split('_1')[0], '1'
    elif 'R1' in filename:
        return filename.split('R1')[0], '1'
    elif '_2' in filename:
        return filename.split('_2')[0], '2'
    elif 'R2' in filename:
        return filename.split('R2')[0], '2'
    assert False, filepath


def download_files(ha_username, ha_password, library_dir, ha_file_path):
    with open(ha_file_path) as hfp:
        for line in hfp:
            line = line.strip()
            if len(line) == 0:
                continue
            slname = line.split('.fastq.gz')[0].split('_')[-1]
            if slname in existing_slnames:
                continue
            url = line.split('http://')[-1]
            url = f'http://{ha_username}:{ha_password}@{url}'
            path = join(library_dir, url.split('/')[-1])
            print(f'{url}\t{path}')


def handle_single_flowcell(ha_username, ha_password,
                           library_dir,
                           metasub_project_name, ha_project_id, flowcell_number,
                           ha_file_path, ha_filename_path):
    existing_file_dir = join(
        ATHENA.METASUB_DATA, metasub_project_name, ha_project_id, flowcell_number
    )
    name_map = parse_filename(ha_filename_path)
    existing_read_files = glob(existing_file_dir + '/*.fastq.gz')
    existing_slnames = set()
    for existing_read_file in existing_read_files:
        root, read_num = get_root_and_read_number(existing_read_file)
        slname = name_map[root]
        existing_slnames.add(slname)
        new_read_filepath = f'{library_dir}/{slname}_{read_num}.fastq.gz'
        print(f'{existing_read_file}\t{new_read_filepath}')
    download_files(ha_username, ha_password, library_dir, ha_file_path)
