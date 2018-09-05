import boto3
import botocore
from os.path import join, dirname, basename, isfile
from os import makedirs
from .constants import WASABI, ATHENA, BRIDGES
from glob import glob


class WasabiBucket:
    """Represents the metasub data bucket on Wasabi (an s3 clone)."""

    def __init__(self, profile_name=None):
        self.session = boto3.Session(profile_name=profile_name)
        self.s3 = self.session.resource('s3', endpoint_url=WASABI.ENDPOINT_URL)
        self.bucket = self.s3.Bucket(WASABI.BUCKET_NAME)

    def list_files(self):
        """Return a list of all files in the bucket."""
        return {key.key for key in self.bucket.objects.all()}

    def upload(self, local_file, remote_key, dryrun):
        print(f'WASABI UPLOADING {result_file} {remote_key}')
        if not dryrun:
            self.bucket.upload_file(local_file, remote_key)

    def download(self, key, local_path, dryrun):
        if type(key) is not str:
            key = key.key
        print(f'WASABI DOWNLOADING {key} {local_path}')
        if not dryrun:
            makedirs(dirname(local_path), exist_ok=True)
            self.bucket.download_file(key, local_path)

    def download_contigs(self,
                         target_dir='assemblies', contig_file='contigs.fasta', dryrun=True):
        """Download contigs."""
        for key in self.bucket.objects.all():
            if 'assemblies' not in key.key or contig_file != basename(key.key):
                continue

            key_path = key.key.split('assemblies/')[1]
            key_dirs = dirname(key_path)
            local_path = join(
                target_dir,
                key_dirs,
                contig_file,
            )
            if isfile(local_path):
                continue
            self.download(key, local_path, dryrun)

    def upload_results(self, result_dir=ATHENA.METASUB_RESULTS, dryrun=True):
        all_uploaded_results = {
            basename(key)
            for key in self.list_files()
            if 'cap_analysis' in key
        }
        for result_file in glob(f'{result_dir}/*/*'):
            if basename(result_file) in all_uploaded_results:
                continue
            tkns = result_file.split('/')
            remote_key = f'cap_analysis/{tkns[-2]}/{tkns[-1]}'
            self.upload(result_file, remote_key, dryrun)

    def upload_contigs(self, result_dir=BRIDGES.ASSEMBLIES, dryrun=True):
        all_uploaded_results = {
            basename(dirname(key))
            for key in self.list_files()
            if 'assemblies' in key
        }
        for result_file in glob(f'{result_dir}/**/*'):
            if basename(dirname(result_file)) in all_uploaded_results:
                continue
            result_root = result_file.split(result_dir)[1]
            remote_key = f'assemblies/{result_root}'
            self.upload(result_file, remote_key, dryrun)