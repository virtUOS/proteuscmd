import argparse
import ipaddress
import json
import pathlib
import requests

__config = None


def config(key):
    '''Access configuration.
    Loading it from the configuration file if not already done.
    '''
    global __config
    if not __config:
        with open(pathlib.Path().home() / '.proteus.json', 'r') as f:
            __config = json.load(f)
    return __config.get(key) if key else __config


def url(path):
    '''Build URL based on configuration.
    '''
    base_url = config('url')
    path = path.lstrip('/')
    return f'{base_url}/Services/REST/v1/{path}'


def login():
    '''Logging in at Proteus.
    '''
    payload = {'username': config('user'), 'password': config('password')}
    result = requests.get(url('login'), params=payload).json()
    token = result.split()[2] + ' ' + result.split()[3]
    return {'Authorization': token, 'Content-Type': 'application/json'}


def getEntitiesByName(auth_header, name, parent, object_type):
    params = {'count': 10,
              'name': name,
              'parentId': parent,
              'start': 0,
              'type': object_type}
    response = requests.get(url('getEntitiesByName'),
                            params=params,
                            headers=auth_header)
    return response.json()


def getEntities(auth_header, parent, object_type):
    params = {'count': 50,
              'parentId': parent,
              'start': 0,
              'type': object_type}
    response = requests.get(url('getEntities'),
                            params=params,
                            headers=auth_header)
    return response.json()


def parse_domain(domain):
    fragments = list(filter(bool, domain.split('.')[::-1]))
    return fragments[:-1], fragments[-1]


def get_requested_views(auth, view_arg):
    # get configuration_id
    data = getEntitiesByName(auth, 'default', 0, 'Configuration')
    configuration_id = data[0]['id']

    views = []

    if view_arg in ('all', 'intern'):
        data = getEntitiesByName(auth, 'intern', configuration_id, 'View')
        views.append(('intern', data[0]['id']))

    if view_arg in ('all', 'extern'):
        data = getEntitiesByName(auth, 'extern', configuration_id, 'View')
        views.append(('extern', data[0]['id']))

    return views


def record_type_from_target(target):
    try:
        ipaddress.ip_address(target)
        return 'HostRecord'
    except ValueError:
        return 'AliasRecord'


def get_record(auth, view, domain):

    zones, host = parse_domain(domain)

    # Navigate through zones
    parent = view
    for zone in zones:
        data = getEntitiesByName(auth, zone, parent, 'Zone')
        if not data:
            zone_path = ' → '.join(zones)
            print(f'Zone {zone_path} could not be found.')
            exit(1)
        parent = data[0]['id']

    # Get host
    data = getEntitiesByName(auth, host, parent, 'HostRecord') \
        + getEntitiesByName(auth, host, parent, 'AliasRecord')
    for record in data:
        properties = record['properties'].split('|')
        for prop in filter(bool, properties):
            print(f'  {prop}')


def set_record(auth, view, domain, target):

    record_type = record_type_from_target(target)

    if record_type == 'HostRecord':
        params = {'absoluteName': domain,
                  'addresses': target,
                  'ttl': -1,
                  'viewId': view}
        response = requests.post(url('addHostRecord'),
                                 params=params,
                                 headers=auth)

    else:  # add aliias record
        params = {'absoluteName': domain,
                  'linkedRecordName': target,
                  'ttl': -1,
                  'viewId': view}
        response = requests.post(url('addAliasRecord'),
                                 params=params,
                                 headers=auth)

    print(response.json())


def delete_record(auth, view, domain):

    zones, host = parse_domain(domain)

    # Navigate through zones
    parent = view
    for zone in zones:
        data = getEntitiesByName(auth, zone, parent, 'Zone')
        parent = data[0]['id']

    # Get host
    data = getEntitiesByName(auth, host, parent, 'HostRecord') \
        or getEntitiesByName(auth, host, parent, 'AliasRecord')
    if not data:
        return

    payload = {'objectId': data[0]['id']}
    result = requests.delete(url('delete'), params=payload, headers=auth)
    print(result)


def main():
    parser = argparse.ArgumentParser(description='Proteus DNS command line')
    parser.add_argument('--view',
                        choices=('all', 'intern', 'extern'),
                        default='all',
                        help='View to operate on')
    parser.add_argument('operation',
                        choices=('get', 'set', 'delete'),
                        help='Operation to perform on domain')
    parser.add_argument('domain',
                        help='Domain to operate on')
    parser.add_argument('target',
                        nargs='?',
                        help='Target of the DNS record')

    args = parser.parse_args()

    if args.operation == 'set' and not args.target:
        parser.error("set requires a target.")

    # Interaction with Proteus
    auth_header = login()
    views = get_requested_views(auth_header, args.view)

    for name, view in views:
        print(name)
        if args.operation == 'get':
            get_record(auth_header, view, args.domain)
        elif args.operation == 'set':
            set_record(auth_header, view, args.domain, args.target)
        elif args.operation == 'delete':
            delete_record(auth_header, view, args.domain)

    # logout from BlueCat
    requests.get(url('logout'), headers=auth_header)


if __name__ == '__main__':
    main()
