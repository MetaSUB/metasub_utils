import pandas as pd
from .constants import METADATA, TABLES


def get_complete_metadata(uploadable=False):
    """Return the complete metadata file as a pandas dataframe."""
    if uploadable:
        return pd.read_csv(METADATA.UPLOADABLE_TABLE_URL, dtype=str, index_col=0)
    return pd.read_csv(METADATA.COMPLETE_TABLE_URL, dtype=str)


def get_canonical_city_names(lower=False):
    """Return a set of canonical city names."""
    city_tbl = pd.read_csv(METADATA.CANONICAL_CITIES_URL, dtype=str)
    city_names = set(city_tbl.ix[:, 0])
    if lower:
        city_names = {city_name.lower() for city_name in city_names}
    return city_names


def as_display_name(name):
    """ Return a name with spaces and first letters capitalized."""
    return ' '.join([
        tkn[:1].upper() + tkn[1:]
        for tkn in name.split('_')
    ])


def parse_sl_table():
    tbl = {}
    with open(TABLES.SL_TABLE) as sl_file:
        for line in sl_file:
            line = line.strip()
            if len(line) == 0:
                continue
            tkns = line.split()
            tbl[tkns[0]] = tkns[1]
    return tbl
