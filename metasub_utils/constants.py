from argparse import Namespace
from os.path import join, dirname


CODE_DIR = dirname(dirname(__file__))


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
ATHENA.METASUB_RESULTS = '/athena/masonlab/scratch/projects/metagenomics/metasub/analysis/new_metasub_cap/.module_ultra/core_results'
ATHENA.METASUB_DATA = '/athena/masonlab/scratch/projects/metagenomics/metasub/data'

# Hudson Alpha
HALPHA = Namespace()
HALPHA.URL = 'http://gsldl.hudsonalpha.org/'
HALPHA.FLOWCELL_FILENAME = join(CODE_DIR, 'tables/hudson_alpha_flowcells.csv')
HALPHA.ATHENA_SL_LIBRARY = join(ATHENA.METASUB_DATA, 'hudson_alpha_library')

# SFTP Server
ZURICH = Namespace()
ZURICH.URL = 'metasub.ethz.ch'
ZURICH.DATA = '/data/'
ZURICH.ASSEMBLIES = '/data/assemblies/'

# BRIDGES
BRIDGES = Namespace()
BRIDGES.METASUB_DATA = '/home/dcdanko/pylon5/MetaSUB'
BRIDGES.ASSEMBLIES = '/home/dcdanko/pylon5/metasub_assemblies'

# Tables
TABLES = Namespace()
TABLES.SL_TABLE = join(CODE_DIR, 'tables/datasuper_to_hauniq.tsv')

# Wasabi
WASABI = Namespace()
WASABI.BUCKET_NAME = 'metasub'
WASABI.ENDPOINT_URL = 'https://s3.wasabisys.com'
