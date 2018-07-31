import pandas as pd
from .constants import METADATA


def get_complete_metadata(uploadable=False):
    """Return the complete metadata file as a pandas dataframe."""
    if uploadable:
        return pd.read_csv(METADATA.UPLAODABLE_TABLE_URL)
    return pd.read_csv(METADATA.COMPLETE_TABLE_URL)


def get_canonical_city_names():
    """Return a set of canonical city names."""
    pass

