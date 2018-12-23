"""Handle tasks on bridges."""

from os.path import join, isfile, basename
from os import makedirs
from shutil import copyfile
from sys import stderr

from metasub_utils.zurich import SFTPKnex
from metasub_utils.zurich.constants import ASSEMBLIES as ZURICH_ASSEMBLIES

from .utils import *


def upload_one_metaspades_dir_to_zurich(server, mspades_dir, sl_tbl):
    hauid_tuple = hauid_from_metaspades_dir(mspades_dir, sl_tbl)
    hauid_sname = '_'.join(hauid_tuple)
    remote_dir = f'{ZURICH_ASSEMBLIES}/{hauid_tuple[0]}/{hauid_tuple[1]}/{hauid_sname}.metaspades/'
    server.make_dirs(remote_dir)
    for subfile in glob(mspades_dir + '/*'):
        if not isfile(subfile):
            continue
        remote_path = remote_dir + basename(subfile)
        server.upload_file(subfile, remote_path)
    misc_dir = remote_dir + 'misc/'
    server.make_dirs(misc_dir)
    for misc_file in glob(mspades_dir + 'misc/*'):
        if not isfile(subfile):
            continue
        remote_path = misc_dir + basename(misc_file)
        server.upload_file(misc_file, remote_path)


def copy_one_metaspades_dir(target_dir, mspades_dir, sl_tbl):
    hauid_tuple = hauid_from_metaspades_dir(mspades_dir, sl_tbl)
    hauid_sname = '_'.join(hauid_tuple)
    target_dir_path = f'{target_dir}/{hauid_tuple[0]}/{hauid_tuple[1]}/{hauid_sname}.metaspades/'
    makedirs(target_dir_path, exist_ok=True)
    for subfile in glob(mspades_dir + '/*'):
        if not isfile(subfile):
            continue
        target_file_path = target_dir_path + basename(subfile)
        if not isfile(target_file_path):
            copyfile(subfile, target_file_path)
    misc_dir = target_dir_path + 'misc/'
    makedirs(misc_dir, exist_ok=True)
    for misc_file in glob(mspades_dir + 'misc/*'):
        if not isfile(subfile):
            continue
        target_file_path = misc_dir + basename(misc_file)
        if not isfile(target_file_path):
            copyfile(misc_file, target_file_path)


def upload_metaspades_assemblies_from_bridges(username, password, dryrun=False):
    sl_tbl = parse_sl_table()
    try:
        server = SFTPKnex(username, password, dryrun=dryrun)
        for metaspades_dir in get_bridges_metaspades_dirs():
            try:
                upload_one_metaspades_dir(server, metaspades_dir, sl_tbl)
            except IndexError:
                print(f'NO_UPLOAD INDEX_ERROR {metaspades_dir}', file=stderr)
            except KeyError:
                print(f'NO_UPLOAD KEY_ERROR {metaspades_dir}', file=stderr)
    finally:
        server.close()


def copy_metaspades_assemblies_from_bridges(target_dir):
    sl_tbl = parse_sl_table()
    for metaspades_dir in get_bridges_metaspades_dirs():
        try:
            copy_one_metaspades_dir(target_dir, metaspades_dir, sl_tbl)
        except IndexError:
            print(f'NO_COPY INDEX_ERROR {metaspades_dir}', file=stderr)
        except KeyError:
            print(f'NO_COPY KEY_ERROR {metaspades_dir}', file=stderr)
