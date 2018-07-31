import pandas as pd
from .constants import METADATA


def get_complete_metadata(uploadable=False):
    """Return the complete metadata file as a pandas dataframe."""
    if uploadable:
        return pd.read_csv(METADATA.UPLAODABLE_TABLE_URL)
    return pd.read_csv(METADATA.COMPLETE_TABLE_URL)


def get_canonical_city_names(lower=False):
    """Return a set of canonical city names."""
    city_tbl = pd.read_csv(METADATA.CANONICAL_CITIES_URL)
    city_names = set(city_tbl.ix[:, 0])
    if lower:
        city_names = {city_name.lower() for city_name in city_names}
    return city_names


def display_name(name):
    """ Return a name with spaces and first letters capitalized."""
    return ' '.join([
        tkn[:1].upper() + tkn[1:]
        for tkn in name.split('_')
    ])
