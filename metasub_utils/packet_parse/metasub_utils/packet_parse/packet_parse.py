
from capalyzer.packet_parser import DataTableFactory
from os import environ
from os.path import join

from .metadata_ontology import add_ontology, clean_city_names


class MetaSUBTableFactory(DataTableFactory):

    def __init__(self, *args, **kwargs):
        super(MetaSUBTableFactory, self).__init__(*args, **kwargs)
        self.metadata = add_ontology(self.metadata)
        self.metadata = clean_city_names(self.metadata)

    @classmethod
    def factory(cls, packet_dir=None, **kwargs):
        """Return a MetaSUBTableFactory filtered for given samples.

        Filter samples based on kwargs, only return the intersection of
        constraints. I.e. air=True, core=True should return no samples.
        """
        if packet_dir is None:
            packet_dir = environ['METASUB_DATA_PACKET_DIR']

        if kwargs.pop('duplicate', False):
            packet_dir = join(packet_dir, 'duplicates')

        if kwargs.pop('control', False):
            packet_dir = join(packet_dir, 'controls')

        base_factory = cls(packet_dir, metadata_tbl='metadata/complete_metadata.csv')
        metadata = base_factory.metadata
        for arg_name, val in kwargs.items():
            if arg_name == 'core':
                metadata = metadata.loc[metadata['control_type_coarse'].isna()]
                metadata = metadata.query('city != "montevideo"')
            else:
                metadata = metadata.query(f'{arg_name} == "{val}"')
        return base_factory.copy(new_metadata=metadata)

    @classmethod
    def all_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over all samples."""
        return cls.factory(packet_dir)

    @classmethod
    def core_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over core samples."""
        return cls.factory(packet_dir, core=True)

    @classmethod
    def control_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over control samples."""
        return cls.factory(packet_dir, control=True)

    @classmethod
    def duplicate_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over duplicate samples."""
        return cls.factory(packet_dir, duplicate=True)

    @classmethod
    def city_factory(cls, city, packet_dir=None, air=False, core=True):
        """Return a MetaSUBTableFactory for core/air samples from a given city."""
        core = not air
        return cls.factory(packet_dir, core=core, city=city)
