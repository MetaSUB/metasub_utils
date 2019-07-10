

NAN = float('nan')


def clean_city_names(metadata, min_count=3):
    """Make all city names lowercase with '_' over ' '."""
    metadata = metadata.copy()
    metadata['city'] = metadata['city'].apply(lambda el: '_'.join(el.lower().split()))
    counts = metadata['city'].value_counts()
    cities = counts[counts >= min_count].index
    metadata = metadata.loc[metadata['city'].isin(cities)]
    return metadata


def add_ontology(metadata):
    """Return a pandas dataframe with metadata and MetaSUB ontologies."""
    metadata = add_surface_ontology(metadata)
    metadata = add_place_ontology(metadata)
    return metadata


def has_keyword(target, *queries):
    try:
        for query in queries:
            if query in target:
                return True
    except TypeError:
        pass
    return False


def add_surface_ontology(metadata):
    """Return a pandas dataframe with metadata and surface ontologies."""
    metadata, tbl = metadata.copy(), {}
    for val in metadata['surface_material'].unique():
        if has_keyword(val, 'glass', 'metal', 'steel', 'copper'):
            tbl[val] = ('metal', 'impermeable')
        elif has_keyword(val, 'stone', 'marble', 'ceramic', 'concrete', 'cement', 'granite'):
            tbl[val] = ('stone', 'impermeable')
        elif has_keyword(val, 'plastic', 'rubber', 'vinyl', 'pvc', 'formica'):
            tbl[val] = ('plastic', 'impermeable')
        elif has_keyword(val, 'fabric', 'cloth', 'carpet'):
            tbl[val] = ('fabric', 'permeable')
        elif has_keyword(val, 'hand', 'flesh', 'wood', 'leather', 'fiber'):
            tbl[val] = ('biological', 'permeable')
        elif has_keyword(val, 'control'):
            tbl[val] = ('control', 'control')
        else:
            tbl[val] = (NAN, NAN)
    metadata['surface_ontology_fine'] = metadata['surface_material'].apply(lambda x: tbl[x][0])
    metadata['surface_ontology_coarse'] = metadata['surface_material'].apply(lambda x: tbl[x][1])
    return metadata


def add_place_ontology(metadata):
    """Return a pandas dataframe with metadata and place ontologies."""
    metadata = metadata.copy()
    metadata['coastal'] = metadata.apply(coastal, reduce=True, axis=1)
    return metadata


def coastal(row):
    if row['coastal_city'] == 'yes':
        return ('coastal', 'coastal')
    if float(row['city_elevation_meters']) > 1000:
        return ('high altitude', 'not_coastal')
    return ('low altitude', 'not_coastal')
