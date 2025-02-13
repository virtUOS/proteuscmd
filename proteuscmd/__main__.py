import click
import ipaddress
import json

from functools import wraps
from proteuscmd.api import Proteus
from proteuscmd.config import proteus_from_config, config
from proteuscmd.types import IP_TYPE, IP_STATE_TYPE, VIEW_TYPE


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


def get_mapped_ip(ip):
    '''Use the mapping configuration to map between IPv4 and IPv6 addresses.
    '''
    for ip_map in (config('v4_v6_map') or []):
        ipv4_network = ipaddress.IPv4Network(ip_map['cidr'])
        ipv6_network = ipaddress.IPv6Network(ip_map['prefix'])
        if ip.version == 4 and ip in ipv4_network:
            int_network_address = int(ipv6_network.network_address)
            int_ip_address = int(ip.ipv6_mapped) & 0xFFFFFFFF
            return ipaddress.IPv6Address(int_network_address | int_ip_address)
        if ip.version == 6 and ip in ipv6_network:
            ipv4_int = int(ip) & 0xFFFFFFFF
            return ipaddress.IPv4Address(ipv4_int)
    raise ValueError(f'No mapping found for IP {ip.compressed}')


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
def dns_get(proteus: Proteus, view, domain):
    '''Get information about a DNS recotd.
    '''
    views = proteus.get_requested_views(view)
    return {name: proteus.get_record(view, domain) for name, view in views}


@dns.command(name='set')
@click.option('--view', **__view_args)
@click.argument('domain')
@click.argument('target', nargs=-1, required=True)
@with_proteus
def dns_set(proteus: Proteus, view, domain, target: list[str]):
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
@click.option('--force/--no-force', default=False, type=bool,
              help='Force will skip any additional confirmation.')
@click.argument('domain')
@with_proteus
def dns_delete(proteus: Proteus, view, force,  domain):
    '''Delete DNS record in Proteus
    '''
    if not force:
        click.confirm(f'Do you really want do delete {domain}?', abort=True)

    views = proteus.get_requested_views(view)
    for name, view in views:
        proteus.delete_record(view, domain)


@ip.command(name='get')
@click.option('--version', required=False, type=int,
              help='IP version to use. '
              'Will use the mapping configuration if necessary.')
@click.argument('ip', type=IP_TYPE)
@with_proteus
def ip_get(proteus: Proteus, version, ip):
    '''Get information about IPv4 address
    '''
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']

    # Map between IPv4 and IPv6 if necessary
    if version and version != ip.version:
        ip = get_mapped_ip(ip)

    data = proteus.get_container_by_ip(ip, conf_id)
    container_id = data["id"]
    return proteus.get_ip_address(ip, container_id)


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
@click.option('--version', required=False, type=int,
              help='IP version to use. '
              'Will use the mapping configuration if necessary.')
@click.argument('ip', type=IP_TYPE)
@click.argument('mac')
@with_proteus
def ip_set(proteus: Proteus, name, admin_email, admin_name, admin_phone,
           comment, state, hostname, view, prop, force, version, ip, mac):
    '''Assign IPv4 or IPv6 address
    '''
    # get notwork information
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']

    # Map between IPv4 and IPv6 if necessary
    if version and version != ip.version:
        ip = get_mapped_ip(ip)

    container_id = proteus.get_container_by_ip(ip, conf_id)['id']

    # check if ip is already reserved
    existing_address = proteus.get_ip_address(ip, container_id)
    if existing_address['id']:
        if not force:
            raise ValueError('IP already reserved')
        proteus.delete_ip_address(ip, container_id)

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

    if ip.version == 4:
        proteus.assign_ip4_address(conf_id, state, ip, mac, props,
                                   hostname, view)
    else:
        proteus.assign_ip6_address(container_id, state, ip, mac, props,
                                   hostname, view)
    return proteus.get_ip_address(ip, container_id)


@ip.command(name='delete')
@click.option('--force/--no-force', default=False, type=bool,
              help='Force will skip any additional confirmation.')
@click.option('--version', required=False, type=int,
              help='IP version to use. '
              'Will use the mapping configuration if necessary.')
@click.argument('ip', type=IP_TYPE)
@with_proteus
def ip_delete(proteus: Proteus, force, version, ip):
    '''Delete assigned IPv4 or IPv6 address
    '''
    # Map between IPv4 and IPv6 if necessary
    if version and version != ip.version:
        ip = get_mapped_ip(ip)

    if not force:
        click.confirm(f'Do you really want do delete {ip}?', abort=True)

    # get notwork information
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']
    container_id = proteus.get_container_by_ip(ip, conf_id)['id']

    proteus.delete_ip_address(ip, container_id)


@ip.command(name='map')
@click.argument('ip', type=IP_TYPE)
def ip_map(ip):
    '''Map between IPv4 and IPv6 addresses.
    '''
    mapped = get_mapped_ip(ip)
    if mapped:
        print(mapped.compressed)


def main():
    cli()


if __name__ == '__main__':
    main()
