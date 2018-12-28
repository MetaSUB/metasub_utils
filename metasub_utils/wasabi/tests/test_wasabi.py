"""Test suite for wasabi."""

from unittest import TestCase
from os import getcwd, mkdir, environ
from os.path import isfile, dirname
from random import randint

from metasub_utils.wasabi import WasabiBucket


def with_aws_credentials(func):
    """Make a default AWS credential file in the home dir."""
    cred_filename = environ['HOME'] + '/.aws/credentials'
    mkdir(dirname(cred_filename), exist_ok=True)

    access_key, secret_key = environ['AWS_ACCESS_KEY'], environ['AWS_SECRET_ACCESS_KEY']
    cred_str = f'[default]\naws_access_key_id={access_key}\naws_secret_access_key={secret_key}\n'
    with open(cred_filename, 'w') as cf:
        cf.write(cred_str)

    return func


class TestWasabi(TestCase):
    """Test suite for wasabi."""

    @with_aws_credentials
    def test_download_file(self):
        bucket = WasabiBucket()
        local_name = f'{getcwd()}/temp_{randint(0, 1000 * 1000)}'
        bucket.download('metasub/Scripts/downloadem.sh', local_name, False)
        bucket.close()
        self.assertTrue(isfile(local_name))
        self.assertTrue(len(open(local_name).read()) > 0)
