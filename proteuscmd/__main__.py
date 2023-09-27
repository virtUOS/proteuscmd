import click
import json

from functools import wraps
from proteuscmd.config import proteus_from_config

__views = click.Choice(('intern', 'extern', 'all'), case_sensitive=False)


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
    Not implemented yet.
    '''
    pass


@dns.command()
@click.option('--view', default='all', type=__views)
@click.argument('domain')
@with_proteus
def get(proteus, view, domain):
    '''Get information about a DNS entry.
    '''
    views = proteus.get_requested_views(view)
    return {name: proteus.get_record(view, domain) for name, view in views}


@dns.command()
@click.option('--view', default='all', type=__views)
@click.argument('domain')
@click.argument('target')
@with_proteus
def set(proteus, view, domain, target):
    '''Set DNS entry in Proteus
    '''
    views = proteus.get_requested_views(view)
    result = {}
    for name, view in views:
        proteus.set_record(view, domain, target)
        result[name] = proteus.get_record(view, domain)
    return result


@dns.command()
@click.option('--view', default='all', type=__views)
@click.argument('domain')
@with_proteus
def delete(proteus, view, domain):
    '''Delete DNS record in Proteus
    '''
    views = proteus.get_requested_views(view)
    for name, view in views:
        proteus.delete_record(view, domain)


if __name__ == '__main__':
    cli()
