#!/usr/bin/python3

import requests
import json

user = ''
password = ''
bam_url = ''

ip = '131.173.23.56'

main_url = "https://" + bam_url + "/Services/REST/v1/"


def login(user, password):
    payload = {'username': user, 'password': password}
    result = requests.get(f'{main_url}login', params=payload).json()
    token = result.split()[2] + ' ' + result.split()[3]
    return {'Authorization':token,'Content-Type':'application/json'}


def getEntitiesByName(auth_header, name, parent, object_type):
    params = {'count': 10,
              'name': name,
              'parentId': parent,
              'start': 0,
              'type': object_type}
    response = requests.get(f'{main_url}getEntitiesByName',
                            params=params,
                            headers=auth_header)
    return response.json()


def getEntities(auth_header, parent, object_type):
    params = {'count': 50,
              'parentId': parent,
              'start': 0,
              'type': object_type}
    response = requests.get(f'{main_url}getEntities',
                            params=params,
                            headers=auth_header)
    return response.json()


def main():
    # login to BlueCat
    auth_header = login(user, password)
    print(auth_header)

    # get configuration_id with getEntitiesByName
    data = getEntitiesByName(auth_header, 'default', 0, 'Configuration')
    print(data)
    configuration_id = data[0]['id']

    # Get extern
    data = getEntitiesByName(auth_header, 'extern', configuration_id, 'View')
    extern = data[0]['id']
    print(data)

    # Get de
    data = getEntitiesByName(auth_header, 'de', extern, 'Zone')
    de = data[0]['id']
    print(data)

    # Get uni-osnabrueck
    data = getEntitiesByName(auth_header, 'uni-osnabrueck', de, 'Zone')
    uni_osnabrueck = data[0]['id']
    print(data)

    # Get hedgedoc
    data = getEntitiesByName(auth_header, 'hedgedoc', uni_osnabrueck, 'HostRecord')
    hedgedoc = data[0]['id']
    print(data)

    # add host record
    params = {'absoluteName': 'lktest.uni-osnabrueck.de',
              'addresses': ip,
              'ttl': -1,
              'viewId': extern}
    response = requests.post(f'{main_url}addHostRecord',
                             params=params,
                             headers=auth_header)
    print(response.json())

    # add aliias record
    params = {'absoluteName': 'lktest2.uni-osnabrueck.de',
              'linkedRecordName': 'vm811.rz.uni-osnabrueck.de',
              'ttl': -1,
              'viewId': extern}
    response = requests.post(f'{main_url}addAliasRecord',
                             params=params,
                             headers=auth_header)
    print(response.json())

    data = getEntitiesByName(auth_header, 'lktest', uni_osnabrueck, 'HostRecord')
    print(data)

    # List all uni-osnabrueck sub-zones
    #data = getEntities(auth_header, uni_osnabrueck, 'Zone')
    #print(data)

    print('######### IP STUFF ####')

    # get range_id with IPRangedByIP
    params = {'address': ip,
              'containerId': configuration_id,
              'type': 'IP4Network'}
    response = requests.get(f'{main_url}getIPRangedByIP',
                            params=params,
                            headers=auth_header)
    data = response.json()
    print(data)
    range_id = data["id"]

    # get properties of IP
    params = {'address': ip, 'containerId': range_id}
    response = requests.get(f'{main_url}getIP4Address',
                            params=params,
                            headers=auth_header)
    data = response.json()
    print(data)

    # logout from BlueCat
    response = requests.get(f'{main_url}logout', headers=auth_header)
    print(response.json())


if __name__ == '__main__':
    main()
