from ..beans.enum import commonPrefs
import os
from .gets import get_and_parse_user_pref
from .base import prefjs_fn
from functools import lru_cache
import warnings

_datadir = None


def setDataDir(path: str):
    """
    call setDataDir(None) to clear cache
    :param path:
    :return:
    """
    global _datadir
    _datadir = path


@lru_cache()
def dataDir(path=None):
    """

    :param path:
    :return:
    """
    global _datadir
    if path is not None:
        _datadir = path
    if _datadir is not None:
        return _datadir

    res = get_and_parse_user_pref(commonPrefs.dataDir, None)
    if res is not None and not os.path.exists(res):
        warnings.warn(f"""
        Cannot find zotero dataDir writed in prefs.js, check your setting in {prefjs_fn()} 
        or report this issue if located path is wrong.
        
        You can set data root manually by call `prefs.common.setDataDir()`
        """)

    if res is None or not os.path.exists(res):
        res = os.path.join(os.path.expanduser('~'), 'Zotero')

    if not os.path.exists(res):
        warnings.warn('cannot find default zotero dataDir, '
                      'will return inexist default dataDir. '
                      'You can set data root manually by call `prefs.common.setDataDir()`')
    return res
