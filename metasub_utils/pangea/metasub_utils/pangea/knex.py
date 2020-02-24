
import requests

ENDPOINT = 'https://pangea.gimmebio.com/api'


class TokenAuth(requests.auth.AuthBase):
    """Attaches MetaGenScope Token Authentication to the given Request object."""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        """Add authentication header to request."""
        request.headers['Authorization'] = f'Token {self.token}'
        return request

    def __str__(self):
        """Return string representation of TokenAuth."""
        return self.token


class Knex:

    def __init__(self):
        self.url = ENDPOINT
        self.auth = None
        self.headers = {'Accept': 'application/json'}

    def login(self, username, password):
        response = requests.post(
            f'{ENDPOINT}/auth/token/login',
            headers=self.headers,
            json={
                'email': username,
                'password': password,
            }
        )
        response.raise_for_status()
        self.auth = TokenAuth(response.json()['auth_token'])
        return self

    def add_org(self, org_name):
        response = requests.post(
            f'{ENDPOINT}/organizations',
            headers=self.headers,
            auth=self.auth,
            json={
                'name': org_name,
            }
        )
        response.raise_for_status()
        return response.json()

    def get_or_add_sample_group(self, group_name, desc):
        groups = self.list_sample_groups()
        grp = [grp for grp in groups if grp['name'] == group_name]
        if grp:
            return grp[0]['uuid']
        return self.add_sample_group(group_name, desc)['uuid']

    def add_sample_group(self, group_name, desc):
        response = requests.post(
            f'{ENDPOINT}/sample_groups',
            headers=self.headers,
            auth=self.auth,
            json={
                'name': group_name,
                'organization': self.metasub_org_uuid,
                'description': desc,
            }
        )
        response.raise_for_status()
        return response.json()

    def add_sample_to_sample_group(self, sample_uuid, group_uuid):
        response = requests.post(
            f'{ENDPOINT}/sample_groups/{group_uuid}/samples',
            headers=self.headers,
            auth=self.auth,
            json={
                'sample_uuid': sample_uuid,
            }
        )
        response.raise_for_status()
        return response.json()

    def list_sample_groups(self):
        response = requests.get(
            f'{ENDPOINT}/sample_groups?format=json',
            headers=self.headers,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()['results']

    def list_organizations(self):
        response = requests.get(
            f'{ENDPOINT}/organizations?format=json',
            headers=self.headers,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()['results']

    def add_sample(self, sample_name, metadata={}):
        response = requests.post(
            f'{ENDPOINT}/samples',
            headers=self.headers,
            auth=self.auth,
            json={
                'name': sample_name,
                'metadata': metadata,
                'library': self.metasub_uuid,
            }
        )
        response.raise_for_status()
        return response.json()

    def add_sample_result(self, sample_uuid, module_name):
        response = requests.post(
            f'{ENDPOINT}/sample_ars',
            headers=self.headers,
            auth=self.auth,
            json={
                'sample': sample_uuid,
                'module_name': module_name,
            }
        )
        response.raise_for_status()
        return response.json()

    def add_sample_result_field(self, ar_uuid, field_name, data):
        response = requests.post(
            f'{ENDPOINT}/sample_ar_fields',
            headers=self.headers,
            auth=self.auth,
            json={
                'analysis_result': ar_uuid,
                'name': field_name,
                'stored_data': data,
            }
        )
        response.raise_for_status()
        return response.json()

    @property
    def metasub_uuid(self):
        return self.get_metasub_library_uuid()

    def get_metasub_library_uuid(self):
        groups = self.list_sample_groups()
        metasub = [grp for grp in groups if grp['name'] == 'MetaSUB'][0]
        return metasub['uuid']

    @property
    def metasub_org_uuid(self):
        return self.get_metasub_org_uuid()

    def get_metasub_org_uuid(self):
        orgs = self.list_organizations()
        metasub = [org for org in orgs if org['name'] == 'MetaSUB Consortium'][0]
        return metasub['uuid']
