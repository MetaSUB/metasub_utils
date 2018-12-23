# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click


@click.group()
def main(args=None):
    """Console script for metasub_utils."""
    pass


try:
    from metasub_utils.wasabi.cli import wasabi
    main.add_command(wasabi)
except ImportError:
    pass


if __name__ == "__main__":
    main()
