import click
import json

from functools import wraps
from proteuscmd.config import proteus_from_config

__views = click.Choice(('intern', 'extern', 'all'), case_sensitive=False)
__ip_states = click.Choice(('STATIC', 'DHCP_RESERVED'), case_sensitive=False)


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
    pass


@cli.group()
def ip():
    '''Register IP addresses.
    '''


@dns.command(name='get')
@click.option('--view', default='all', type=__views)
@click.argument('domain')
@with_proteus
def dns_get(proteus, view, domain):
    '''Get information about a DNS recotd.
    '''
    views = proteus.get_requested_views(view)
    return {name: proteus.get_record(view, domain) for name, view in views}


@dns.command(name='set')
@click.option('--view', default='all', type=__views)
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
@click.option('--view', default='all', type=__views)
@click.argument('domain')
@with_proteus
def dns_delete(proteus, view, domain):
    '''Delete DNS record in Proteus
    '''
    views = proteus.get_requested_views(view)
    for name, view in views:
        proteus.delete_record(view, domain)


@ip.command(name='get')
@click.argument('ip')
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
@click.option('--admin-email', '-e', required=True)
@click.option('--admin-name', '-n', required=True)
@click.option('--admin-phone', '-p', required=True)
@click.option('--comment', '-c')
@click.option('--state', '-s', default='DHCP_RESERVED', type=__ip_states)
@click.option('--hostname', '-h')
@click.option('--view', default='all', type=__views)
@click.option('--prop', default=[], multiple=True)
@click.option('--force/--no-force', default=False, type=bool)
@click.argument('ip')
@click.argument('mac')
@with_proteus
def ip_set(proteus, admin_email, admin_name, admin_phone, comment, state,
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
    for extra_prop in prop:
        k, v = extra_prop.split('=', 1)
        props[k] = v
    props = {k: v for k, v in props.items() if v}

    proteus.assign_ip_address(conf_id, state, ip, mac, props, hostname, view)
    return proteus.get_ip4_address(ip, range_id)


@ip.command(name='delete')
@click.argument('ip')
@with_proteus
def ip_delete(proteus, ip):
    '''Delete assigned IPv4 address
    '''
    # get notwork information
    data = proteus.get_entities_by_name('default', 0, 'Configuration')
    conf_id = data[0]['id']
    range_id = proteus.get_ip_range_by_ip(ip, conf_id)['id']

    proteus.delete_ip4_address(ip, range_id)


if __name__ == '__main__':
    cli()
