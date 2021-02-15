# This file used to read Zotero Profile
# see https://www.zotero.org/support/kb/profile_directory
from typing import Dict
from .base import prefjs_fn, try_parse_pref
import re

match_user_pref = re.compile("""user_pref\("([^"]+)", (.+)\);""")

__all__ = [
    'get_and_parse_user_prefs',
    'get_and_parse_user_pref',
    'search_user_prefs'
]


# user_pref("extensions.zotero.export.quickCopy.setting", "export=9cb70025-a888-4a29-a210-93ec52da40d4");
def _get_user_prefs() -> Dict[str, str]:
    """
    saved in <proile_directory>/prefs.js, get raw value
    :return:
    """
    prof = {}
    with open(prefjs_fn(), 'r') as r:
        for line in r:
            res = re.search(match_user_pref, line)
            if res is not None:
                prof[res.group(1)] = res.group(2)
    return prof


def search_user_prefs(keylike: str) -> dict:
    user_prefs = _get_user_prefs()
    keylike = keylike.replace('.', '').lower()
    return {
        k: try_parse_pref(user_prefs[k])
        for k in user_prefs if keylike in k.lower()
    }


def get_user_pref(key, default=None) -> str:
    """

    :return:
    """
    return _get_user_prefs().get(key, default)


def get_and_parse_user_pref(key: str, default=""):
    value = _get_user_prefs().get(key, default)  # type:str
    return try_parse_pref(value)


def get_and_parse_user_prefs():
    prefs = _get_user_prefs()
    return {k: try_parse_pref(v) for k, v in prefs.items()}
