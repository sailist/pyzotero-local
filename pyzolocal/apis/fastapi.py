try:
    import fastapi
except:
    raise ModuleNotFoundError('fastapi not found, run '
                              '     pip install fastapi'
                              ' to install it')
from .. import __version__
from .base import get_sql_api_map, get_prefs_api_map
from fastapi import FastAPI
from functools import wraps


def get_fastapis():
    app = FastAPI(title='zotero-local', version=__version__)
    sql_api_map = get_sql_api_map()

    def res_wrap(func):
        @wraps(func)
        def inner(*args):
            return {
                'code': 200,
                'result': func(),
                'msg': ''
            }

        return inner

    for name, func in sql_api_map.items():
        wrap_func = res_wrap(func)
        path = f'/db/{name}'
        _ = app.get(path)(wrap_func)

    prefs_api_map = get_prefs_api_map()
    for name, func in prefs_api_map.items():
        wrap_func = res_wrap(func)
        path = f'/pref/{name}'
        _ = app.get(path)(wrap_func)

    return app
