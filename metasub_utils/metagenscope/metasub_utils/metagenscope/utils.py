"""Utilities for MetaGenScope."""


def as_display_name(name):
    """ Return a name with spaces and first letters capitalized."""
    return ' '.join([
        tkn[:1].upper() + tkn[1:]
        for tkn in name.split('_')
    ])
