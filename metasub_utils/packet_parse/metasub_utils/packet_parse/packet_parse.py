
from capalyzer.packet_parser import DataTableFactory
from os import environ

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
        base_factory = cls(packet_dir, metadata_tbl='metadata/complete_metadata.csv')
        metadata = base_factory.metadata
        for arg_name, val in kwargs.items():
            if arg_name == 'core':
                arg_name = 'core_project'
                val = 'core' if val else 'not_core'
            if arg_name == 'air':
                if val:
                    metadata = metadata.query(f'project == "CSD17_AIR"')
                continue
            metadata = metadata.query(f'{arg_name} == "{val}"')
        return base_factory.copy(new_metadata=metadata)

    @classmethod
    def core_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over core samples."""
        return cls.factory(packet_dir, core=True)

    @classmethod
    def air_factory(cls, packet_dir=None):
        """Return a MetaSUBTableFactory over air samples."""
        return cls.factory(packet_dir, air=True)

    @classmethod
    def city_factory(cls, city, packet_dir=None, air=False, core=False):
        """Return a MetaSUBTableFactory for core/air samples from a given city."""
        core = not air
        return cls.factory(packet_dir, core=core, air=air, city=city)
