import json
import pathlib

from proteuscmd.api import Proteus

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


def proteus_from_config():
    '''Load configuration file and use it to initialize the proteus client.
    '''
    cfg = config('user'), config('password'), config('url'), config('replace')
    return Proteus(*cfg)
