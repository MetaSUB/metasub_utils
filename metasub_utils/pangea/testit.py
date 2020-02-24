
import os
import random
from metasub_utils.pangea.knex import Knex


k = Knex().login('dcdanko@gmail.com', os.environ['PANGEA_PASS'])

print(k.list_sample_groups())
print(k.metasub_uuid)
print('Get Operations Working')


def random_replicate_name(len=12):
    """Return a random alphanumeric string of length `len`."""
    out = random.choices('abcdefghijklmnopqrtuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ0123456789', k=len)
    return ''.join(out)

replicate = random_replicate_name()

print(k.add_org(f'test_add_org_from_cli_{replicate}'))
print(k.add_sample(f'test_add_sample_from_cli_{replicate}', metadata={'foo': 'bar'}))
print('Post Operations Working')
