import logging

from src import internalconf, ui
from flatten_dict import flatten, unflatten
import json
import os

def config_path(filename):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', filename)

def load_config(filename):
    with open(config_path(filename), 'r') as f:
        return json.loads(f.read())

class Config:

    def __init__(self, configfile: str, fix_values, fix_missing, write=False):
        """
        Creates a config object from a json file
        :param configfile: the config filename (json)
        :param fix_values: a function to resolve values of the wrong type
        :param fix_missing: a function to resolve missing values
        :param write: writes changes (fix_values and fix_missing function results) to the file
        """
        parsed = load_config(configfile)
        flat = flatten(parsed, 'path')
        alloweds = flatten(internalconf.CONFIG_TYPES, 'path')
        buffer = dict()

        for key, _type in alloweds.items():
            if key not in flat.keys() or key is None:
                value = fix_missing(key)
            elif type(flat[key]) is not _type:
                value = fix_values(key)
            else:
                value = flat[key]

            buffer[key] = value

        if write:
            with open(config_path(configfile), 'w') as f:
                logging.info("Writing changes to the config file...")
                f.write(json.dumps(unflatten(buffer, 'path'), indent=4))

        self._dict = buffer

    def get(self, what):
        try:
            ret = self._dict[what]
        except KeyError:
            logging.fatal(f'Setting "{what}" is not declared')

        if 'path' in what or 'file' in what:
            ret = os.path.normpath(os.path.expanduser(ret))

        return ret


def wizard(configfile=None, write=False):
    configdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')

    if configfile not in os.listdir(configdir):
        if configfile is None:
            if ui.ask("No config file has been supplied. Wanna create a new one?",choices='yn'):
                configfile = input("config/")
                with open(config_path(configfile), 'w') as f:
                    f.write('{}')
                write = True
            else:
                configfile = 'config.json'
        else:
            logging.fatal(f'File "{configfile}" does not exist! Create one in "{configdir}"')

    def ask(key):
        # print(f"Oops! The setting '{key}' is not properly configured.")
        value = input(f"{key} = ")
        if value in internalconf.CFGWIZ_TRUES:
            return True
        elif value in internalconf.CFGWIZ_FALSES:
            return False
        elif internalconf.CFGWIZ_LISTS.match(value):
            return internalconf.CFGWIZ_LISTS.findall(value)
        else:
            return value


    return Config(configfile, fix_values=ask, fix_missing=ask, write=write)