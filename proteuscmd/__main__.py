import argparse
import json
import pathlib

from proteuscmd.api import Proteus

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
    cfg = config('user'), config('password'), config('url'), config('replace')
    with Proteus(*cfg) as proteus:
        views = proteus.get_requested_views(args.view)

        for name, view in views:
            print(name)
            if args.operation == 'get':
                print('\n'.join(proteus.get_record(view, args.domain)))
            elif args.operation == 'set':
                print(proteus.set_record(view, args.domain, args.target))
            elif args.operation == 'delete':
                print(proteus.delete_record(view, args.domain))


if __name__ == '__main__':
    main()
