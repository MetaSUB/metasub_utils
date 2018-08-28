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

from .constants import HALPHA, ATHENA
from glob import glob
from os import makedirs
from os.path import join, basename, dirname, isfile
from concurrent.futures import ThreadPoolExecutor
import requests
from sys import stderr


###############################################################################
"""
Make migrations from current (aug 22, 2018) state of Athena to new HA Library based state.
"""


def rename_one_sl_path_to_ha_unique(filepath):
    tkns = filepath.split('/')
    ha_project_id, flowcell_number, file_base = tkns[-3], tkns[-2], tkns[-1]
    new_file_base = f'{ha_project_id}_{flowcell_number}_{file_base}'
    new_filepath = join(dirname(filepath), new_file_base)
    return new_filepath


def rename_sl_names_to_ha_unique():
    for filepath in glob(HALPHA.ATHENA_SL_LIBRARY + '/*/*/SL*.fastq.gz'):
        new_filepath = rename_one_sl_path_to_ha_unique(filepath)
        if not isfile(new_filepath):
            print(f'{filepath} {new_filepath}')


def map_from_name_in_datasuper_to_ha_unique(source_fastqs_file):
    name_map = {}
    for line in source_fastqs_file:
        if len(line.strip()) == 0:
            continue
        tkns = line.split()
        if '1.fastq' not in tkns[0]:
            continue
        ds_name = basename(tkns[0]).split('_1.')[0].split('.R1.')[0]
        try:
            ha_unique = basename(rename_one_sl_path_to_ha_unique(tkns[1])).split('_1.fastq.gz')[0]
        except IndexError:
            print('!!! ' + line, file=stderr)
        assert ds_name not in name_map
        name_map[ds_name] = ha_unique
    return name_map


def rename_existing_core_results(source_fastqs_file, old_result_dir):
    name_map = map_from_name_in_datasuper_to_ha_unique(source_fastqs_file)
    path_map = {}
    for filepath in glob(old_result_dir + '/*/*'):
        old_name = basename(filepath).split('.')[0]
        try:
            new_name = name_map[old_name]
        except KeyError:
            print(f'!!! {old_name}', file=stderr)
            continue
        new_path = 'new_metasub_cap'.join(filepath.split('metasub_cap'))
        new_path = new_name.join(new_path.split(old_name))
        path_map[filepath] = new_path
    return path_map


###############################################################################

"""
Download data from Hudson Alpha.
"""


def download_file(url, path, auth):
    r = requests.get(url, auth=auth)
    open(path, 'wb').write(r.content)


def process_flowcells(dryrun, ha_auth):
    with open(HALPHA.FLOWCELL_FILENAME) as flowcell_file:
        tkn_gen = (
            line.strip().split(',')
            for line in flowcell_file
            if len(line.strip()) > 0
        )
        for metasub_project_name, _, ha_project_id, ha_file_url in tkn_gen:
            flowcell_number = ha_file_url.split('files_')[-1].split('.txt')[0]
            ha_file_url = HALPHA.URL + ha_file_url
            ha_filename_url = 'filenames'.join(ha_file_url.split('files'))
            library_dir = join(HALPHA.ATHENA_SL_LIBRARY, ha_project_id, flowcell_number)
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


def parse_filename(ha_filename_path):
    name_map = {}
    with open(ha_filename_path) as hfp:
        hfp.readline()
        hfp.readline()
        for line in hfp:
            line = line.strip()
            if len(line) == 0:
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


def get_root_and_read_number(filepath):
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


def download_files(dryrun, ha_auth, library_dir, ha_file_path, existing_slnames):
    executor = ThreadPoolExecutor(max_workers=50)
    futures = []
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
                futures.append(executor.submit(lambda : download_file(url, path, ha_auth)))
    for future in futures:
        future.result()


def handle_single_flowcell(dryrun, ha_auth,
                           library_dir,
                           metasub_project_name, ha_project_id, flowcell_number,
                           ha_file_path, ha_filename_path):
    existing_file_dir = join(
        ATHENA.METASUB_DATA, metasub_project_name, ha_project_id, flowcell_number
    )
    name_map = parse_filename(ha_filename_path)
    existing_read_files = glob(existing_file_dir + '/*.fastq.gz')
    names_in_library = set()
    for in_library in glob(library_dir + '/*.fastq.gz'):
        try:
            root, _ = get_root_and_read_number(in_library)
        except AssertionError:
            continue
        names_in_library.add(root)
    existing_slnames = set()
    for existing_read_file in existing_read_files:
        try:
            root, read_num = get_root_and_read_number(existing_read_file)
        except AssertionError:
            print(f'UNKNOWN\t{existing_read_file}')
            continue
        slname = name_map[root]
        if slname in names_in_library:
            continue
        existing_slnames.add(slname)
        new_read_filepath = f'{library_dir}/{slname}_{read_num}.fastq.gz'
        print(f'COPY\t{existing_read_file}\t{new_read_filepath}')
    download_files(dryrun, ha_auth, library_dir, ha_file_path, existing_slnames | names_in_library)
