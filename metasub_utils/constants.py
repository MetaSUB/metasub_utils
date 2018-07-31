from argparse import Namespace

# Metadata
METADATA = Namespace()
METADATA.COMPLETE_TABLE_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/complete_metadata.csv'
METADATA.UPLOADABLE_TABLE_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/upload_metadata.csv'
METADATA.CANONICAL_CITIES_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/spreadsheets/city_names.csv'


# MetaGenScope
METAGENSCOPE = Namespace()
METAGENSCOPE.MSUB_GROUP_NAME = 'MetaSUB'


# Columns
COLUMNS = Namespace()
COLUMNS.BC = 'barcode'
COLUMNS.METASUB_NAME = 'metasub_name'
COLUMNS.HA_ID = 'ha_id'
COLUMNS.SL_NAME = 'sl_name'
COLUMNS.CITY = 'city'
COLUMNS.IDS = set(
    [COLUMNS.HA_ID, COLUMNS.BC, COLUMNS.METASUB_NAME, COLUMNS.SL_NAME]
)


# Athena
ATHENA = Namespace()
ATHENA.METASUB_RESULTS = '/athena/masonlab/scratch/projects/metagenomics/metasub/analysis/metasub_cap/.module_ultra/core_results'
