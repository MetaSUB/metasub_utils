import pysftp
from .constants import *


class SFTPKnex:

    def __init__(self, username, password, dryrun=False):
        self.dryrun = dryrun
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        self.knex = pysftp.Connection(URL, username=username, password=password, cnopts=cnopts)

    def close(self):
        self.knex.close()

    def __enter__(self):
        pass

    def __exit__(self):
        return self.close()

    def upload_file(self, localpath, remotepath):
        print(f'[SFTP Knex] UPLOAD {localpath} {remotepath}')
        if self.dryrun:
            return
        self.knex.put(localpath, remotepath=remotepath)

    def make_symlink(self, source_path, target_path):
        print(f'[SFTP Knex] SYMLINK {source_path} {target_path}')
        if self.dryrun:
            return
        self.knex.symlink(source_path, target_path)

    def make_dirs(self, remote_dirs):
        print(f'[SFTP Knex] MAKEDIRS {remote_dirs}')
        if self.dryrun:
            return
        self.knex.makedirs(remote_dirs)
