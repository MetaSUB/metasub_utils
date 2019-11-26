"""
Procedure for handling data from HA:
1. Each new flowcell url should be recorded in 'hudson_alpha_flowcells.csv'
   along with its metasub_project_name, and H.A. project names
2. A new 'library' directory should be created as <library_top>/<HA project ID>/<flowcell number>
3. The relevant file and filenames files hould be downloaded to this dir
4. All fragmented files should be downloaded to the new dir
5. All fragmented files should be concatenated within the dir and the fragments deleted.
   Each file should now be given a name of the form
   <HA project ID>_<flowcell number>_<SL number>_[1,2].fastq.gz
   The predicate of this name is the HA Unique ID

---
Procedure for back mapping results to HALib
1. Make a map from current name to the HA Unique ID
2. Build a table mapping old files to new names
3. move and link back old files to new names
"""

from glob import glob
from os import makedirs
from os.path import join, basename, dirname, isfile
from concurrent.futures import ThreadPoolExecutor

from .constants import *
from .utils import download_file, parse_flowcell_table, get_root_and_read_number


def process_flowcells(dryrun, ha_auth):
    flowcells = parse_flowcell_table()
    for metasub_project_name, _, ha_project_id, date, ha_file_url in flowcells:
        flowcell_number = ha_file_url.split('files_')[-1].split('.txt')[0]
        ha_file_url = URL + ha_file_url
        ha_filename_url = 'filenames'.join(ha_file_url.split('files'))
        library_dir = join(ATHENA_SL_LIBRARY, ha_project_id, flowcell_number)
        makedirs(library_dir, exist_ok=True)

        ha_file_path = join(library_dir, ha_file_url.split('/')[-1])
        download_file(ha_file_url, ha_file_path, ha_auth)
        ha_filename_path = join(library_dir, ha_filename_url.split('/')[-1])
        download_file(ha_filename_url, ha_filename_path, ha_auth)
        handle_single_flowcell(
            dryrun, ha_auth,
            library_dir,
            metasub_project_name, ha_project_id, flowcell_number,
            ha_file_path, ha_filename_path
        )


def download_files(dryrun, ha_auth, library_dir, ha_file_path, existing_ha_uids):
    existing_slnames = {hauid.split('_')[-1] for hauid in existing_ha_uids}
    executor, futures = ThreadPoolExecutor(max_workers=50), []
    with open(ha_file_path) as hfp:
        for line in hfp:
            line = line.strip()
            if len(line) == 0:
                continue
            slname = line.split('.fastq.gz')[0].split('_')[-1]
            if slname in existing_slnames:
                continue
            url = line
            path = join(library_dir, url.split('/')[-1])
            if isfile(path):
                continue
            print(f'DOWNLOAD\t{url}\t{path}')
            if not dryrun:
                futures.append(executor.submit(lambda: download_file(url, path, ha_auth)))
    for future in futures:
        future.result()


def handle_single_flowcell(dryrun, ha_auth,
                           library_dir,
                           metasub_project_name, ha_project_id, flowcell_number,
                           ha_file_path, ha_filename_path):
    names_in_library = set()
    for in_library in glob(library_dir + '/*.fastq.gz'):
        try:
            root, _ = get_root_and_read_number(in_library)
            names_in_library.add(root)
        except AssertionError:
            continue
    download_files(dryrun, ha_auth, library_dir, ha_file_path, names_in_library)
