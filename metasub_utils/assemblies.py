from glob import glob
from .constants import BRIDGES, ZURICH
from os.path import join, dirname, isfile, basename
from os import makedirs
from shutil import copyfile
from .utils import parse_sl_table
from .sftp_server import SFTPKnex
from sys import stderr


def hauid_from_metaspades_dir(contig_path, sl_tbl):
    tkns = contig_path.split('haib')[1].split('/')
    haib = 'haib' + tkns[0]
    flowcell = tkns[1]
    raw_id = tkns[2].split('_1.fastq.gz.metaspades')[0].split('.R1.fastq.gz.metaspades')[0]
    sl_id = sl_tbl[raw_id].split('_')[2]
    return haib, flowcell, sl_id


def get_bridges_metaspades_dirs():
    contig_files = glob(BRIDGES.METASUB_DATA + '/**/contigs.fasta', recursive=True)
    metaspades_dirs = {
        dirname(contig_file)
        for contig_file in contig_files
    }
    return metaspades_dirs


def upload_one_metaspades_dir(server, mspades_dir, sl_tbl):
    hauid_tuple = hauid_from_metaspades_dir(mspades_dir, sl_tbl)
    hauid_sname = '_'.join(hauid_tuple)
    remote_dir = f'{ZURICH.ASSEMBLIES}/{hauid_tuple[0]}/{hauid_tuple[1]}/{hauid_sname}.metaspades/'
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
