"""Constants for working with MetaSUB Metadata."""

COMPLETE_TABLE_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/complete_metadata.csv'
UPLOADABLE_TABLE_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/upload_metadata.csv'
CANONICAL_CITIES_URL = 'https://raw.githubusercontent.com/dcdanko/MetaSUB-metadata/master/spreadsheets/city_names.csv'


HAUID = 'hudson_alpha_uid'
HA_ID = 'ha_id'
METASUB_NAME = 'metasub_name'
SL_NAME = 'sl_name'
OTHER_PROJ_UID = 'other_project_uid'
BC = 'barcode'
IDS = set([HAUID, HA_ID, BC, METASUB_NAME, SL_NAME, OTHER_PROJ_UID])
