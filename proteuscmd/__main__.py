import argparse

from proteuscmd.config import proteus_from_config

__config = None


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
    with proteus_from_config() as proteus:
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
