import click
import ipaddress
import socket

from proteuscmd.config import config


class ConfigOption(click.Option):
    def handle_parse_result(self, ctx, opts, args):
        # If the option is not provided in the command line,
        # try to get it from the global config
        if self.name and self.name not in opts and config(self.name):
            opts = dict(opts)
            opts[self.name] = config(self.name)

        # Call the parent class's handle_parse_result to continue
        return super(ConfigOption, self).handle_parse_result(ctx, opts, args)


class IPType(click.ParamType):
    '''Click parameter type for IPv4 or IPv6 address.
    Also accepts domain names if they can be resolved to an IP address.
    '''
    name = 'IPv4 or IPv6 address'

    def convert(self, value, param, ctx):
        try:
            return ipaddress.ip_address(value)
        except ValueError:
            pass

        try:
            return ipaddress.ip_address(socket.gethostbyname(value))
        except socket.gaierror:
            pass

        self.fail(f'{value!r} cannot be resolved to IPv4 or IPv6 address',
                  param, ctx)


IP_TYPE = IPType()

VIEW_TYPE = click.Choice(('intern', 'extern', 'all'), case_sensitive=False)

IP_STATE_TYPE = click.Choice(('STATIC', 'DHCP_RESERVED'), case_sensitive=False)
