import click
import json

from functools import wraps
from proteuscmd.config import proteus_from_config
from proteuscmd.types import IPV4_TYPE, IP_STATE_TYPE, VIEW_TYPE


__view_args = {
        'default': 'all',
        'type': VIEW_TYPE,
        'help': 'DNS view structure to operate in'}


def with_proteus(f):
    '''Provide a Proteus client as first parameter of the wraped function.
    Print the result if one exists.
    '''
    @wraps(f)
    def decorated(*args, **kwargs):
        with proteus_from_config() as proteus:
            data = f(proteus, *args, **kwargs)
        if data:
            print(json.dumps(data, indent=2))
    return decorated


@click.group()
def cli():
    pass


@cli.group()
def dns():
    '''Get information about or update DNS entries.
    '''


@cli.group()
def ip():
    '''Register IP addresses.
    '''


@dns.command(name='get')
@click.option('--view', **__view_args)
@click.argument('domain')
@with_proteus
def dns_get(proteus, view, domain):
    '''Get information about a DNS recotd.
    '''
    views = proteus.get_requested_views(view)
    return {name: proteus.get_record(view, domain) for name, view in views}


@dns.command(name='set')
@click.option('--view', **__view_args)
@click.argument('domain')
@click.argument('target')
@with_proteus
def dns_set(proteus, view, domain, target):
    '''Set DNS record in Proteus
    '''
    views = proteus.get_requested_views(view)
    result = {}
    for name, view in views:
        proteus.set_record(view, domain, target)
        result[name] = proteus.get_record(view, domain)
    return result


@dns.command(name='delete')
@click.option('--view', **__view_args)
@click.argument('domain')
@with_proteus
def dns_delete(proteus, view, domain):
    '''Delete DNS record in Proteus
    '''
    views = proteus.get_requested_views(view)
    for name, view in views:
        proteus.delete_record(view, domain)


@ip.command(name='get')
@click.argument('ip', type=IPV4_TYPE)
@with_proteus
def ip_get(proteus, ip):
    '''Get information about IPv4 address
    '''
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']

    data = proteus.get_ip_range_by_ip(ip, conf_id)
    range_id = data["id"]

    return proteus.get_ip4_address(ip, range_id)


@ip.command(name='set')
@click.option('--name', required=False,
              help='Name of the host. Defaults to hostname if set.')
@click.option('--admin-email', '-e', required=True,
              help='Email address of the host admin')
@click.option('--admin-name', '-n', required=True,
              help='Name of the host admin')
@click.option('--admin-phone', '-p', required=True,
              help='Phone number of the host admin')
@click.option('--comment', '-c',
              help='Comment to add to the address registration')
@click.option('--state', '-s', default='DHCP_RESERVED', type=IP_STATE_TYPE,
              help='Type of IP assignment')
@click.option('--hostname', '-h',
              help='Hostname to add as DNS record for the assigned IP address')
@click.option('--view', **__view_args)
@click.option('--prop', default=[], multiple=True,
              help='Additional properties in the form of property=value')
@click.option('--force/--no-force', default=False, type=bool,
              help='If to overwrite existing IP assignments')
@click.argument('ip', type=IPV4_TYPE)
@click.argument('mac')
@with_proteus
def ip_set(proteus, name, admin_email, admin_name, admin_phone, comment, state,
           hostname, view, prop, force, ip, mac):
    '''Assign IPv4 address
    '''
    # get notwork information
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']
    range_id = proteus.get_ip_range_by_ip(ip, conf_id)['id']

    # check if ip is already reserved
    existing_address = proteus.get_ip4_address(ip, range_id)
    if existing_address['id']:
        if force:
            proteus.delete_ip4_address(ip, range_id)
        else:
            raise ValueError('IP already reserved')

    # prepare properties
    props = {'admin_email': admin_email,
             'admin_name': admin_name,
             'admin_phone': admin_phone,
             'comment': comment}
    if name or hostname:
        # Name defaults to hostname
        props['name'] = name or hostname
    for extra_prop in prop:
        k, v = extra_prop.split('=', 1)
        props[k] = v
    props = {k: v for k, v in props.items() if v}

    proteus.assign_ip_address(conf_id, state, ip, mac, props, hostname, view)
    return proteus.get_ip4_address(ip, range_id)


@ip.command(name='delete')
@click.argument('ip', type=IPV4_TYPE)
@with_proteus
def ip_delete(proteus, ip):
    '''Delete assigned IPv4 address
    '''
    # get notwork information
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']
    range_id = proteus.get_ip_range_by_ip(ip, conf_id)['id']

    proteus.delete_ip4_address(ip, range_id)


def main():
    cli()


if __name__ == '__main__':
    main()
