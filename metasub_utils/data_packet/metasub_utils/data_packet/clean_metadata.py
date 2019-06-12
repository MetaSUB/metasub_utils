
import pandas as pd


NAN = float('nan')
lab_controls = {
    ('zymoshield_tube', 'lab_negative_control', 'barcode'): ['235159589', '235162224', '235163966'],
    ('zymoshield_media_tube', 'lab_negative_control', 'barcode'): ['235196487', '232022683', '235078676'],
    ('zymoshield_swab_tube', 'lab_negative_control', 'barcode'): ['235163072', '235161887', '235162222'],
    ('zymoshield_media_swab_tube', 'lab_negative_control', 'barcode'): ['235196528', '232021956', '232021998'],
    ('zymoshield_positive_control', 'positive_control', 'barcode'): ['235082297'],

    ('bench_pre_bleach', 'background_control', 'uuid'): ['BarcelonaNov2018_MS011'],
    ('bench_post_bleach', 'background_control', 'uuid'): ['BarcelonaNov2018_MS012'],

    ('mobiome_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS039', 'BarcelonaNov2018_MS045', 'BarcelonaNov2018_MS051'],
    ('mobiome_media_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS040', 'BarcelonaNov2018_MS046', 'BarcelonaNov2018_MS052'],
    ('mobiome_media_pellet_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS041', 'BarcelonaNov2018_MS047', 'BarcelonaNov2018_MS053'],

    ('mobiome_positive_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS036', 'BarcelonaNov2018_MS042', 'BarcelonaNov2018_MS048'],
    ('mobiome_positive_media_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS043', 'BarcelonaNov2018_MS037', 'BarcelonaNov2018_MS049'],
    ('mobiome_positive_media_pellet_swab', 'lab_negative_control', 'uuid'): ['BarcelonaNov2018_MS038', 'BarcelonaNov2018_MS044', 'BarcelonaNov2018_MS050'],

    ('background_control', 'background_control', 'metasub_name'): ['CSD16-BCN-132', 'CSD16-BCN-070', 'CSD16-BCN-006'],

    ('zymo_extraction_lab_water_negative_control', 'lab_negative_control', 'ha_id'): ['5080-CEM-0079', '5080-CEM-0080', '5080-CEM-0081'],
    ('zymo_extraction_positive_control', 'positive_control', 'ha_id'): ['5080-CEM-0078'],
    ('zymo_extraction_diluted_positive_control', 'positive_control', 'ha_id'): ['5080-CEM-0082', '5080-CEM-0083'],

    ('background_control', 'background_control', 'barcode'): [
        '235030889',
        '235030329',
        '235030339',
        '235030333',
        '235030330',
        '235030331',
        '235030334',
        '235030332',
        '235030897',
        '235030360',
        '235030326',
        '235030336',
        '235030894',
        '235030895',
        '235030343',
        '235030899',
        '235030893',
        '235030327',
        '235030359',
        '235030337',
        '235030342',
        '235030389',
        '235030398',
        '235030368',
        '235030413',
        '235030381',
        '235030412',
        '235030366',
        '235030354',
        '235030374',
        '235030351',
        '235030347',
        '235030375',
        '235030344',
        '235030371',
        '235030350',
        '235030352',
        '235030349',
        '235030382',
        '235030364',
        '235030386',
        '235030365',
        '235030383',
        '235030384',
        '235030387',
        '235030353',
        '235030385',
        '235030363',
        '235030372',
        '235030346',
        '235030356',
        '235030367',
        '235030379',
        '235030369',
        '235030377',
        '235030380',
        '235030362',
        '235030355',
        '235030376',
        '235030370',
        '235030378',
        '235030357',
        '235029400',
        '235030361',
        '235030362',
        '235030355',
        '235030376',
        '235030370',
        '235030378',
        '235030357',
        '235029400',
        '235030361',
        '235030415',
        '235030420',
        '235030414',
        '235030401',
        '235030411',
        '235030417',
        '235030393',
        '235030404',
        '235030395',
        '235030407',
        '235030403',
        '235030373',
        '235030409',
        '235030394',
        '235030390',
        '235030408',
        '235030419',
        '235030405',
        '235030416',
        '235030402',
        '235030397',
        '235029421',
    ],
}


def contains_pattern(s, *args):
    for arg in args:
        if s and isinstance(s, str) and (arg.lower() in s.lower()):
            return True
    return False


def normalize_control(row):
    ctrl = row['control_type']
    if not ctrl:
        return None
    if ctrl in ['ctrl cities']:
        return 'background_control'
    if ctrl in ['positive_control', 'poszymo']:
        return 'positive_control'
    if ctrl in ['negative_control', 'dry tube', 'dry tube & swab', 'tube & rna/dna out', 'tube & rna/dna out & swab']:
        return 'lab_negative_control'
    return None


def id_control(row, col):
    if row[col]:
        return row[col]
    msub_name = row['metasub_name']
    if contains_pattern(msub_name, 'positive'):
        return 'positive_control'
    elif contains_pattern(msub_name, 'control', 'copan'):
        return 'background_control'
    if contains_pattern(row['surface_material'], 'negative_control', 'air'):
        return 'background_control'
    if contains_pattern(row['city'], 'neg_control'):
        return 'background_control'
    if contains_pattern(row['city'], 'pos_control'):
        return 'positive_control'


def add_lab_controls_fine(row):
    for (fine, coarse, col), samples in lab_controls.items():
        if contains_pattern(row[col], *samples):
            return fine


def add_lab_controls_coarse(row):
    for (fine, coarse, col), samples in lab_controls.items():
        if contains_pattern(row[col], *samples):
            return coarse


def controlify(tbl):
    tbl['control_type_fine'] = tbl.apply(add_lab_controls_fine, axis=1)
    tbl['control_type_coarse'] = tbl.apply(add_lab_controls_fine, axis=1)

    tbl['control_type_fine'] = tbl.apply(lambda r: id_control(r, 'control_type_fine'), axis=1)
    tbl['control_type_coarse'] = tbl.apply(lambda r: id_control(r, 'control_type_coarse'), axis=1)

    tbl['control_type_coarse'] = tbl.apply(normalize_control, axis=1)
    return tbl


def add_surface_ontology(metadata):
    """Return a pandas dataframe with metadata and surface ontologies."""
    metadata, tbl = metadata.copy(), {}
    for val in metadata['surface_material'].unique():
        if contains_pattern(val, 'glass', 'metal', 'steel', 'copper'):
            tbl[val] = ('metal', 'impermeable')
        elif contains_pattern(val, 'stone', 'marble', 'ceramic', 'concrete', 'cement', 'granite'):
            tbl[val] = ('stone', 'impermeable')
        elif contains_pattern(val, 'plastic', 'rubber', 'vinyl', 'pvc', 'formica'):
            tbl[val] = ('plastic', 'impermeable')
        elif contains_pattern(val, 'fabric', 'cloth', 'carpet'):
            tbl[val] = ('fabric', 'permeable')
        elif contains_pattern(val, 'hand', 'flesh', 'wood', 'leather', 'fiber'):
            tbl[val] = ('biological', 'permeable')
        elif contains_pattern(val, 'control'):
            tbl[val] = ('control', 'control')
        else:
            tbl[val] = (NAN, NAN)
    metadata['surface_ontology_fine'] = metadata['surface_material'].apply(lambda x: tbl[x][0])
    metadata['surface_ontology_coarse'] = metadata['surface_material'].apply(lambda x: tbl[x][1])
    return metadata


def add_place_ontology(metadata):
    """Return a pandas dataframe with metadata and place ontologies."""
    metadata = metadata.copy()
    metadata['coastal'] = metadata.apply(lambda r: coastal(r)[1], reduce=True, axis=1)
    metadata['city_elevation'] = metadata.apply(lambda r: coastal(r)[0], reduce=True, axis=1)
    return metadata


def coastal(row):
    if row['coastal_city'] == 'yes':
        return ('coastal', 'coastal')
    if float(row['city_elevation_meters']) > 1000:
        return ('high_altitude', 'not_coastal')
    return ('low_altitude', 'not_coastal')


def deduper(row, mems, col='ha_id'):
    if row[col] and isinstance(row[col], str) and (row[col] in mems):
        return False
    mems.add(row[col])
    return True


def clean_metadata_table(tbl):
    """Return a tuple of (clean metadata, control-metadata, duplicate-metadata, duplicate-map).

    All values are pandas dataframes/series.
    """
    tbl = tbl.query('project != "CSD17_AIR"')
    tbl['city'] = tbl['city'].map(lambda val: 'honolulu' if val == 'antarctica' else val)
    tbl = controlify(tbl)
    tbl = add_surface_ontology(tbl)
    tbl = add_place_ontology(tbl)

    mems = set()
    deduped = tbl.loc[tbl.apply(lambda r: deduper(r, mems), axis=1)]
    cntrls = deduped.loc[~deduped['control_type_coarse'].isna()]
    mems = set()
    dupes = tbl.loc[tbl.apply(lambda r: not deduper(r, mems), axis=1)]
    dupe_primary = deduped.loc[deduped['ha_id'].isin(dupes['ha_id']), ['uuid', 'ha_id']]

    dupe_map = dupe_primary.join(
        dupes[['uuid', 'ha_id']].set_index('ha_id'),
        on='ha_id', how='outer', lsuffix='_primary', rsuffix='_secondary'
    )
    dupe_map = dupe_map[['uuid_primary', 'uuid_secondary', 'ha_id']]

    return deduped, cntrls, dupes, dupe_map
