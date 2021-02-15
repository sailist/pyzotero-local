import platform
import json
import configparser
import os
from functools import lru_cache


def is_win():
    return 'windows' in platform.platform().lower()


def is_mac():
    # TODO
    raise NotImplementedError()


def is_linux():
    raise NotImplementedError()
    # return 'linux' in platform.platform().lower()


def read_profile_path(fn):
    """
    load profile path from profiles.ini
    :param fn:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(fn)
    if len(config.sections()) == 2:
        prof_key = config.sections()[-1]
    else:
        if config['General']['startwithlastprofile'] == '1':
            prof_key = config.sections()[-1]
        else:
            raise NotImplementedError()
    return config[prof_key]['Path']


def profile_root():
    user_root = os.path.expanduser('~')
    if is_win():
        zotero_root = os.path.join(user_root, r'AppData\Roaming\Zotero\Zotero')
    elif is_linux():
        zotero_root = os.path.join(user_root, '.zotero/zotero')
    elif is_mac():
        zotero_root = os.path.join(user_root, 'Library/Application Support/Zotero')
    else:
        raise NotImplementedError()
    return zotero_root


def prefs_root():
    user_root = os.path.expanduser('~')
    zotero_root = profile_root()
    if is_win():
        prof_relroot = read_profile_path(os.path.join(zotero_root, 'profiles.ini'))
        return os.path.join(zotero_root, prof_relroot)
    elif is_linux():
        zotero_root = os.path.join(user_root, '.zotero/zotero')
    elif is_mac():
        zotero_root = os.path.join(user_root, 'Library/Application Support/Zotero')
    else:
        raise NotImplementedError()


@lru_cache(1)
def prefjs_fn():
    return os.path.join(prefs_root(), 'prefs.js')


def try_parse_pref(value: str):
    if value is None:
        return value

    if value.startswith('"'):
        value = value.strip('"')
        if value[0] in "[{":
            value = value.replace('\\', '')
            try:
                value = json.loads(value)
            except:
                pass
        return value
    else:
        if value in {'false', 'true'} or value.isnumeric():
            return eval(value.title())

    return value
