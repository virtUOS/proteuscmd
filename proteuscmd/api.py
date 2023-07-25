import ipaddress
import requests


class Proteus:

    __user: str = ''
    __password: str = ''
    __base_url: str = ''
    __replacements: dict[str, str] = {}
    __auth_header: dict[str, str] = {}

    def __init__(self, user, password, base_url, replacements):
        self.__user = user
        self.__password = password
        self.__base_url = base_url
        self.__replacements = replacements

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def __url(self, path):
        '''Build URL based on configuration.
        '''
        path = path.lstrip('/')
        return f'{self.__base_url}/Services/REST/v1/{path}'

    def __post(self, path, params):
        response = requests.post(self.__url(path),
                                 params=params,
                                 headers=self.__auth_header)
        return response.json()

    def __get(self, path, params):
        response = requests.get(self.__url(path),
                                params=params,
                                headers=self.__auth_header)
        return response.json()

    def __delete(self, path, params):
        return requests.delete(self.__url('delete'),
                               params=params,
                               headers=self.__auth_header)

    def login(self):
        '''Logging in at Proteus.
        '''
        payload = {'username': self.__user, 'password': self.__password}
        result = requests.get(self.__url('login'), params=payload).json()
        token = result.split()[2] + ' ' + result.split()[3]
        self.__auth_header = {
                'Authorization': token,
                'Content-Type': 'application/json'}

    def logout(self):
        '''Logout from BlueCat
        '''
        self.__get('logout', {})

    def get_entities_by_name(self, name, parent, object_type):
        params = {'count': 10,
                  'name': name,
                  'parentId': parent,
                  'start': 0,
                  'type': object_type}
        return self.__get('getEntitiesByName', params)

    def get_entities(self, parent, object_type):
        params = {'count': 50,
                  'parentId': parent,
                  'start': 0,
                  'type': object_type}
        return self.__get('getEntities', params)

    def assign_ip_address(self, conf_id, status, ip, mac, properties):
        status = status.upper()
        if status not in ['STATIC', 'RESERVED', 'DHCP_RESERVED']:
            raise Exception(f'Invalid status: {status}')

        props = '|'.join([f'{k}={v}' for k, v in properties.items()])

        params = {'action': f'MAKE_{status}',
                  'configurationId': conf_id,
                  'ip4Address': ip,
                  'macAddress': mac,
                  'properties': props}
        response = self.__post('assignIP4Address', params)

        if response.status_code != 200:
            raise Exception(response.text)

    def get_ip_range_by_ip(self, ip, conf_id):
        params = {'address': ip,
                  'containerId': conf_id,
                  'type': 'IP4Network'}
        return self.__get('getIPRangedByIP', params=params)

    def get_ip4_address(self, ip, range_id):
        params = {'address': ip, 'containerId': range_id}
        return self.__get('getIP4Address', params=params)

    def parse_domain(self, domain):
        for src, to in self.__replacements.items():
            domain = domain.replace(src, to)
        fragments = list(filter(bool, domain.split('.')[::-1]))
        return fragments[:-1], fragments[-1]

    def get_requested_views(self, view_arg):
        '''Get requested views.
        view_arg can be intern, extern or all.
        It controls if this will return the view intern, extern or both.
        '''
        # get configuration_id
        data = self.get_entities_by_name('default', 0, 'Configuration')
        conf_id = data[0]['id']

        views = []

        if view_arg in ('all', 'intern'):
            data = self.get_entities_by_name('intern', conf_id, 'View')
            views.append(('intern', data[0]['id']))

        if view_arg in ('all', 'extern'):
            data = self.get_entities_by_name('extern', conf_id, 'View')
            views.append(('extern', data[0]['id']))

        return views

    def record_type_from_target(self, target):
        '''Return type of record based on the target.
        HostRecord if the target is an IP address,
        AliasRecord if it is a domain
        '''
        try:
            ipaddress.ip_address(target)
            return 'HostRecord'
        except ValueError:
            return 'AliasRecord'

    def get_record(self, view, domain):
        '''Get record for domain in specified view.
        '''

        zones, host = self.parse_domain(domain)

        # Navigate through zones
        parent = view
        for zone in zones:
            data = self.get_entities_by_name(zone, parent, 'Zone')
            if not data:
                zone_path = ' → '.join(zones)
                raise Exception(f'Zone {zone_path} could not be found.')
            parent = data[0]['id']

        # Get host
        data = self.get_entities_by_name(host, parent, 'HostRecord') \
            + self.get_entities_by_name(host, parent, 'AliasRecord')
        for record in data:
            properties = record['properties'].split('|')
            return [prop for prop in filter(bool, properties)]
        return []

    def set_record(self, view, domain, target):

        record_type = self.record_type_from_target(target)

        if record_type == 'HostRecord':
            params = {'absoluteName': domain,
                      'addresses': target,
                      'ttl': -1,
                      'viewId': view}
            return self.__post('addHostRecord', params)

        else:  # add aliias record
            params = {'absoluteName': domain,
                      'linkedRecordName': target,
                      'ttl': -1,
                      'viewId': view}
            return self.__post('addAliasRecord', params)

    def delete_record(self, view, domain):

        zones, host = self.parse_domain(domain)

        # Navigate through zones
        parent = view
        for zone in zones:
            data = self.get_entities_by_name(zone, parent, 'Zone')
            parent = data[0]['id']

        # Get host
        data = self.get_entities_by_name(host, parent, 'HostRecord') \
            or self.get_entities_by_name(host, parent, 'AliasRecord')
        if not data:
            return

        payload = {'objectId': data[0]['id']}
        result = self.__delete('delete', payload)
        return result
