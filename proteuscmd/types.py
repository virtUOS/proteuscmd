import click
import ipaddress
import socket


class IPType(click.ParamType):
    '''Click parameter type for IPv4 or IPv6 address.
    Also accepts domain names if they can be resolved to an IP address.
    '''
    name = 'IPv4 or IPv6 address'

    def convert(self, value, param, ctx):
        try:
            return ipaddress.ip_address(value)
        except ipaddress.AddressValueError:
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
