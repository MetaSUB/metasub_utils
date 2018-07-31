from .utils import get_complete_metadata, get_canonical_city_names
from tempfiles import NamedTemporaryFile
from .constants import COLUMNS


def run_cmd(cmd):
    print(cmd)


def get_sample_names(city_name):
    """Return a list of sample names for the city."""
    metadata = get_complete_metadata()
    sample_names = set()
    for _, row in metadata.iterrows():
        if row[COLUMNS.CITY].lower() != city_name.lower():
            continue
        for id_name in COLUMNS.IDS:
            sample_names.add(row[COLMNS.IDS])
    return sample_names


def build_file_manifest(result_dir, sample_names):
    """Return the name of a temp file of filepaths from the given city."""
    files = [
        fpath
        for sample_name in sample_names
        for fpath in glob(result_dir + '/' + sample_name + '/*')
        if isfile(fpath)
    ]
    city_metadata_file_handle = NamedTemporaryFile(delete=False)
    for fpath in files:
        city_metadata_file_handle.write(f'{fpath}\n')
    city_metadata_file_handle.close()
    return city_metadata_file_handle.name()


def build_metadata_table(city_name):
    """Return the name of a temp file with metadata from the given city."""
    metadata = get_complete_metadata(uploadable=True)
    city_metadata = metadata[metadata[COLUMNS.CITY].lower() == city_name.lower()]
    city_metadata_file_handle = NamedTemporaryFile(delete=False)
    city_metadata_file = city_metadata_file_handle.name()
    city_metadata_file_handle.close()
    city_metadata.to_csv(city_metadata_file)

    return city_metadata_file


def upload_city(result_dir, city_name, upload_only=False):
    """Upload a city to MGS and run middleware."""
    assert city_name in get_canonical_city_names()
    sample_names = get_sample_names(city_name)
    file_manifest = build_file_manifest(result_dir, sample_names)
    upload_files_cmd = f'metagenscope upload files -g "{city_name}" -m {file_manifest}'
    run_cmd(upload_files_cmd)
    file_manifest.delete()

    city_metadata_table = build_metadata_table(city_name)
    sample_name_str = ' '.join(sample_names)
    upload_metadata_cmd = f'metagenscope upload metadata {city_metadata_table} {sample_name_str}'
    run_cmd(upload_metadata_cmd)
    city_metadata_table.delete()

    if upload_only:
        return
    group_middleware_cmd = f'metagenscope run middleware group "{city_name}"'
    run_cmd(upload_metadata_cmd)
    for sample_name in sample_names:
        sample_middleware_cmd = f'metagenscope run middleware sample {sample_name}'
        run_cmd(sample_name)
