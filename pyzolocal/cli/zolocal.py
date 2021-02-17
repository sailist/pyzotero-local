from fire import Fire

from pyzolocal.prefs.base import (
    prefs_root, prefjs_fn, profile_root,
    is_mac, is_win, is_linux
)
from pyzolocal.prefs.common import dataDir
from pyzolocal.files.base import storage_root
from pyzolocal import __version__


def main(*args, **kwargs):
    if len(args) == 0 and len(kwargs) == 0:
        version_display = (f'''pyzolocal version {__version__}
        |Win: {is_win()}|MAC: {is_mac()}|Linue: {is_linux()}| 
        zotero.profile_directory = {profile_root()}
        zotero.dataDir = {dataDir()}
        ''')
        print(version_display)


Fire(main)
exit(0)
