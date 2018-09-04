import boto3
import botocore
from os.path import join, dirname, basename, isfile
from os import makedirs
from .constants import WASABI



class WasabiBucket:
    """Represents the metasub data bucket on Wasabi (an s3 clone)."""


    def __init__(self, profile_name=None):
        self.session = boto3.Session(profile_name=profile_name)
        self.s3 = self.session.resource('s3', endpoint_url=WASABI.ENDPOINT_URL)
        self.bucket = self.s3.Bucket(WASABI.BUCKET_NAME)


    def list_files(self):
        """Return a list of all files in the bucket."""
        return set([key.key for key in self.bucket.objects.all()])


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
            print(f'WASABI DOWNLOADING {key.key} {local_path}')
            if not dryrun:
                makedirs(dirname(local_path), exist_ok=True)
                self.bucket.download_file(key.key, local_path)
