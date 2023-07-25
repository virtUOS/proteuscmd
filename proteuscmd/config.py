import json
import pathlib

__config = None


def config(key: str):
    '''Access configuration.
    Loading it from the configuration file if not already done.
    '''
    global __config
    if not __config:
        with open(pathlib.Path().home() / '.proteus.json', 'r') as f:
            __config = json.load(f)
    return __config.get(key)
