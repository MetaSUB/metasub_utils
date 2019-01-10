"""Test suite for wasabi."""

from unittest import TestCase
from os import getcwd, makedirs, environ
from os.path import isfile, dirname
from random import randint

from metasub_utils.wasabi import WasabiBucket


def test_with_aws_credentials(func):
    """Make a default AWS credential file in the home dir."""
    cred_filename = environ['HOME'] + '/.aws/credentials'
    if isfile(cred_filename):
        return
    makedirs(dirname(cred_filename), exist_ok=True)

    access_key, secret_key = environ['AWS_ACCESS_KEY'], environ['AWS_SECRET_ACCESS_KEY']
    cred_str = f'[default]\naws_access_key_id={access_key}\naws_secret_access_key={secret_key}\n'
    with open(cred_filename, 'w') as cf:
        cf.write(cred_str)

    return func


class TestWasabi(TestCase):
    """Test suite for wasabi."""

    @test_with_aws_credentials
    def test_download_file(self):
        bucket = WasabiBucket()
        local_name = f'{getcwd()}/temp_{randint(0, 1000 * 1000)}'
        bucket.download('Scripts/downloadem.sh', local_name, False)
        bucket.close()
        self.assertTrue(isfile(local_name))
        self.assertTrue(len(open(local_name).read()) > 0)

    @test_with_aws_credentials
    def test_list_raw(self):
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(city_name='paris')
        bucket.close()
        self.assertTrue(raw_reads)

    @test_with_aws_credentials
    def test_list_from_project(self):
        """Test that we can filter sample names by project."""
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(project_name='tigress')
        bucket.close()
        self.assertTrue(len(raw_reads) == 2 * 83)

    @test_with_aws_credentials
    def test_list_from_city_project(self):
        """Test that we can filter sample names by city and project."""
        bucket = WasabiBucket()
        raw_reads = bucket.list_raw(city_name='swansea', project_name='tigress')
        bucket.close()
        self.assertTrue(len(raw_reads) == 2 * 6)

    @test_with_aws_credentials
    def test_download_from_city_project(self):
        """Test that we do not get an obvious error on download."""
        bucket = WasabiBucket()
        bucket.download_raw(city_name='swansea', project_name='tigress')
        bucket.close()
