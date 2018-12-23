"""Make migrations from (aug 22, 2018) state of Athena to new HA Library based state."""


def rename_one_sl_path_to_ha_unique(filepath):
    tkns = filepath.split('/')
    ha_project_id, flowcell_number, file_base = tkns[-3], tkns[-2], tkns[-1]
    new_file_base = f'{ha_project_id}_{flowcell_number}_{file_base}'
    new_filepath = join(dirname(filepath), new_file_base)
    return new_filepath


def rename_sl_names_to_ha_unique():
    for filepath in glob(ATHENA_SL_LIBRARY + '/*/*/SL*.fastq.gz'):
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
