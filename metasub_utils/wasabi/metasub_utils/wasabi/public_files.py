
from os.path import basename, dirname, join

from metasub_utils.metadata import get_samples_from_city


def list_public_files():
    """Return a list of all public files."""
    public_file_filename = join(dirname(__file__), 'metasub_public_files.txt')
    out = []
    with open(public_file_filename, 'r') as f:
        for line in f:
            out.append(line.strip())
    return out


def list_nonhuman_reads(sample_names=None, city_name=None, project_name=None, grouped=False):
    samples = set()
    if city_name or project_name:
        samples |= set(get_samples_from_city(city_name, project_name=project_name))
    if sample_names:
        samples |= set(sample_names)
    nonhuman_reads = [
        filename for filename in list_public_files()
        if 'nonhuman_read' in filename and '/human_filtered_data/' in filename
    ]
    nonhuman_read_files = {}
    for nonhuman_read in nonhuman_reads:
        sname = basename(nonhuman_read).split('.')[0]
        if samples and sname not in samples:
            continue
        nonhuman_read_files[sname] = sorted([nonhuman_read] + nonhuman_read_files.get(sname, []))

    raw_list = []
    for read_files in nonhuman_read_files.values():
        if not grouped:
            raw_list += read_files
        else:
            raw_list.append(read_files)
    return raw_list
