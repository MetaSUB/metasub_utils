"""Functions for handling metadata."""

import pandas as pd

from .constants import UPLOADABLE_TABLE_URL, COMPLETE_TABLE_URL, CANONICAL_CITIES_URL


def get_complete_metadata(uploadable=False):
    """Return the complete metadata file as a pandas dataframe."""
    if uploadable:
        return pd.read_csv(UPLOADABLE_TABLE_URL, dtype=str, index_col=0)
    return pd.read_csv(COMPLETE_TABLE_URL, dtype=str, index_col=0)


def get_canonical_city_names(lower=False):
    """Return a set of canonical city names."""
    city_tbl = pd.read_csv(CANONICAL_CITIES_URL, dtype=str)
    city_names = set(city_tbl.ix[:, 0])
    if lower:
        city_names = {city_name.lower() for city_name in city_names}
    return city_names


def get_samples_from_city(city_name, project_name=None):
    """Return a list of sample names from a particular city.

    If city_name is False return a list with all sample names.
    """
    metadata = get_complete_metadata()
    filtered = metadata
    if city_name:
        city_name = city_name.lower()
        filtered = filtered[filtered['city'] == city_name]
    if project_name:
        project_name = project_name.upper()
        filtered = filtered[filtered['project'] == project_name]
    return list(filtered.index)
