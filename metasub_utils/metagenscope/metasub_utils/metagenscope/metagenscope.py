from glob import glob
from os.path import isfile
from subprocess import call
from .utils import (
    get_complete_metadata,
    get_canonical_city_names,
    as_display_name,
)
from tempfile import NamedTemporaryFile
from .constants import COLUMNS, METAGENSCOPE


def run_cmd(cmd, dryrun=True):
    print(cmd)
    if dryrun:
        return
    call(cmd, shell=True)


def get_sample_names(city_names):
    """Return a list of sample names for the city."""
    city_names = [city_name.lower() for city_name in city_names]
    metadata = get_complete_metadata()
    sample_names = set()
    for row_id, row in metadata.iterrows():
        if str(row[COLUMNS.CITY]).lower() not in city_names:
            continue
        sample_names.add(row['hudson_alpha_uid'])
    return sample_names


def build_file_manifest(result_dir, sample_names):
    """Return the name of a temp file of filepaths from the given city."""
    files = []
    sample_names_with_files = set()
    for sample_name in sample_names:
        for fpath in glob(result_dir + '/' + sample_name + '/*'):
            if isfile(fpath):
                files.append(fpath)
                sample_names_with_files.add(sample_name)
    city_metadata_file_handle = NamedTemporaryFile(mode='w', delete=False)
    for fpath in files:
        city_metadata_file_handle.write(f'{fpath}\n')
    city_metadata_file_handle.close()
    return city_metadata_file_handle.name, sample_names_with_files


def build_metadata_table(city_names):
    """Return the name of a temp file with metadata from the given city."""
    metadata = get_complete_metadata(uploadable=True)
    city_metadata_rows = metadata[COLUMNS.CITY].str.lower().isin(city_names)
    city_metadata = metadata[city_metadata_rows]
    city_metadata_file_handle = NamedTemporaryFile(suffix='.csv', mode='w', delete=False)
    city_metadata_file = city_metadata_file_handle.name
    city_metadata_file_handle.close()
    city_metadata.to_csv(city_metadata_file)

    return city_metadata_file


def upload_cities(result_dir, city_names, display_name, upload_only=False, dryrun=True):
    """Upload a city to MGS and run middleware."""
    city_names = {city_name.lower() for city_name in city_names}
    assert len(city_names & get_canonical_city_names(lower=True)) == len(city_names)

    sample_names = get_sample_names(city_names)
    file_manifest, sample_names = build_file_manifest(result_dir, sample_names)
    upload_files_cmd = f'metagenscope upload files -g "{display_name}" -m {file_manifest}'
    run_cmd(upload_files_cmd, dryrun=dryrun)

    city_metadata_table = build_metadata_table(city_names)
    sample_name_str = ' '.join(sample_names)
    upload_metadata_cmd = f'metagenscope upload metadata {city_metadata_table} {sample_name_str}'
    run_cmd(upload_metadata_cmd, dryrun=dryrun)

    add_group_cmd = f'metagenscope add group-to-org "{display_name}" {METAGENSCOPE.MSUB_GROUP_NAME}'
    run_cmd(add_group_cmd, dryrun=dryrun)

    if upload_only:
        return
    group_middleware_cmd = f'metagenscope run middleware group "{display_name}"'
    run_cmd(group_middleware_cmd, dryrun=dryrun)
    for sample_name in sample_names:
        sample_middleware_cmd = f'metagenscope run middleware samples {sample_name}'
        run_cmd(sample_middleware_cmd, dryrun=dryrun)
