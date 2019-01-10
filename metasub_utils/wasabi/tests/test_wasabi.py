"""Test suite for wasabi."""

from unittest import TestCase
from os import getcwd, makedirs, environ
from os.path import isfile, dirname
from random import randint

from functools import wraps

from metasub_utils.wasabi import WasabiBucket


def with_aws_credentials(func):
    """Make a default AWS credential file in the home dir."""
    @wraps(func)
    def decorated_function(self, *args, **kwargs):
        cred_filename = environ['HOME'] + '/.aws/credentials'
        if isfile(cred_filename):
            return
        makedirs(dirname(cred_filename), exist_ok=True)

        access_key, secret_key = environ['AWS_ACCESS_KEY'], environ['AWS_SECRET_ACCESS_KEY']
        creds = f'[default]\naws_access_key_id={access_key}\naws_secret_access_key={secret_key}\n'
        with open(cred_filename, 'w') as cf:
            cf.write(creds)

        return func(self, *args, **kwargs)

    return decorated_function


class TestWasabi(TestCase):
    """Test suite for wasabi."""

    @with_aws_credentials
    def test_download_file(self):
        bucket = WasabiBucket()
        local_name = f'{getcwd()}/temp_{randint(0, 1000 * 1000)}'
        bucket.download('Scripts/downloadem.sh', local_name, False)
        bucket.close()
        self.assertTrue(isfile(local_name))
        self.assertTrue(len(open(local_name).read()) > 0)

    @with_aws_credentials
    def test_list_raw(self):
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(city_name='paris')
        bucket.close()
        self.assertTrue(raw_reads)

    @with_aws_credentials
    def test_list_from_project(self):
        """Test that we can filter sample names by project."""
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(project_name='tigress')
        bucket.close()
        self.assertTrue(len(raw_reads) == 2 * 83)

    @with_aws_credentials
    def test_list_from_city_project(self):
        """Test that we can filter sample names by city and project."""
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(city_name='swansea', project_name='tigress')
        bucket.close()
        self.assertTrue(len(raw_reads) == 2 * 6)

    @with_aws_credentials
    def test_download_from_city_project(self):
        """Test that we do not get an obvious error on download."""
        bucket = WasabiBucket()
        bucket.download_raw(city_name='swansea', project_name='tigress')
        bucket.close()
