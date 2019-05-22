import os
import re

SCHEME_FILTERS = ["slug"]
CONFIG_TYPES = {
    "paths": {
        "dirs": {
            "videos": str,
            "audios": str,
            "covers": str
        },
        "renamed": {
            "videos": str,
            "audios": str,
            "covers": str
        },
        "files":  {
            "videos": str,
            "audios": str,
            "covers": str
        },
        "misc": {
            "track_data": str
        },
        "ftp": {
            "videos": str,
            "audios": str,
            "covers": str
        }
    },
    "titles": {
        "track": str,
        "single": str,
        "remix": str,
        "ep": str,
        "album": str,
        "videos": str
    },
    "defaults": {
        "artist": str,
        "covers-description":str
    },
    "options": {
        "automatic":{
            "recover":bool,
            "open-dirs":bool,
            "create-dirs":bool,
        },
        "show-help":bool,
        "confirm": {
            "track-title":bool,
            "track-number":bool,
            'rename-tracks':bool,
            "apply-metadata":bool,
        }
    },
    "description":{
      "languages":list,
      "file":str
    }
}

# cfgwiz = config wizard
CFGWIZ_TRUES = 'True true yes on'.split(' ')
CFGWIZ_FALSES = 'False false no off'.split(' ')
CFGWIZ_LISTS = re.compile('\[?(?:([^,]+,))+\]?')
LOG_SHOW_MODULE = True

LOG_FORMAT = ("[{levelname:>8}@{module}.{funcName}:{lineno}]" if LOG_SHOW_MODULE else '[{levelname:^8}]') + " {message}"

LATEST_TRACKDATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'latest.json')