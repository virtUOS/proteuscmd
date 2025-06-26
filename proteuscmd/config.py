import json
import pathlib
import subprocess  # nosec blacklist

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
    password = config('password')
    if not password:
        password_cmd = config('password_cmd')
        password = subprocess.run(password_cmd,  # nosec B602
                                  shell=type(password_cmd) is str,
                                  capture_output=True,
                                  text=True,
                                  check=True).stdout
    cfg = config('user'), password, config('url'), config('replace')
    return Proteus(*cfg)
