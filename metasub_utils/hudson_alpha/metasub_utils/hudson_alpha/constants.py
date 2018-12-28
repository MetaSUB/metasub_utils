"""Constants for downloading data from the Hudson Alpha Sequencing Center."""

from os.path import join, dirname

from metasub_utils.athena.constants import METASUB_DATA as ATHENA_METASUB_DATA

URL = 'http://gsldl.hudsonalpha.org/'
FLOWCELL_FILENAME = join(dirname(__file__), 'hudson_alpha_flowcells.csv')
ATHENA_SL_LIBRARY = join(ATHENA_METASUB_DATA, 'hudson_alpha_library')
