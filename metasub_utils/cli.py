# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click
from sys import stderr

VERBOSE = True


@click.group()
def main(args=None):
    """Console script for metasub_utils."""
    pass


sub_clis = [
    ('metasub_utils.athena.cli', 'athena'),
    ('metasub_utils.bridges.cli', 'bridges'),
    ('metasub_utils.hudson_alpha.cli', 'hudsonalpha'),
    ('metasub_utils.metadata.cli', 'metadata'),
    ('metasub_utils.metagenscope.cli', 'mgs'),
    ('metasub_utils.wasabi.cli', 'wasabi'),
]


def add_submodule_cli(module_name, cli_main_name):
    try:
        cli_module = __import__(module_name, fromlist=[''])
        main.add_command(getattr(cli_module, cli_main_name))
    except ImportError:
        if VERBOSE:
            print(f'Unable to import {module_name}', file=stderr)


for module_name, cli_main_name in sub_clis:
    add_submodule_cli(module_name, cli_main_name)


if __name__ == "__main__":
    main()
