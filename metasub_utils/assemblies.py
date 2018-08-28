from glob import glob
from .constants import BRIDGES, ZURICH
from os.path import join, dirname, isfile, basename
from .utils import parse_sl_table
from .sftp_server import SFTPKnex


def hauid_from_metaspades_dir(contig_path, sl_tbl):
    tkns = contig_path.split('haib')[1].split('/')
    haib = 'haib' + tkns[0]
    flowcell = tkns[1]
    raw_id = tkns[2].split('_1.fastq.gz.metaspades')[0]
    sl_id = sl_tbl[raw_id].split('_')[2]
    return haib, flowcell, sl_id


def get_bridges_metaspades_dirs():
    contig_files = glob(BRIDGES.METASUB_DATA + '/**/contigs.fasta')
    metaspades_dirs = {
        dirname(contig_file)
        for contig_file in contig_files
    }
    return metaspades_dirs


def upload_one_metaspades_dir(server, mspades_dir, sl_tbl):
    hauid_tuple = hauid_from_metaspades_dir(mspades_dir, sl_tbl)
    hauid_sname = '_'.join(hauid)
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


def upload_metaspades_assemblies_from_bridges(username, password, dryrun=False):
    sl_tbl = parse_sl_table()
    server = SFTPKnex(username, password, dryrun=dryrun)
    for metaspades_dir in get_bridges_metaspades_dirs():
        upload_one_metaspades_dir(server, metaspades_dir, sl_tbl)
