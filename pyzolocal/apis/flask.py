try:
    import flask
except:
    raise ModuleNotFoundError('fastapi not found, run '
                              '     pip install fastapi'
                              ' to install it')
from .. import __version__
from .base import get_sql_api_map, get_prefs_api_map
from flask import Flask
from flask import jsonify
from flask import request

from functools import wraps


def _create_url_link(name, path):
    return f'<div><a href="{path}">{name}</a></div>'


def _doc_route(api_list):
    api_list = "\n".join(api_list)

    def wrap():
        return f'<div>{api_list}<div>'

    return wrap


def get_flaskapis():
    app = Flask(import_name='zotero-local')
    sql_api_map = get_sql_api_map()

    def res_wrap(func):
        @wraps(func)
        def inner(*args):
            return jsonify({
                'code': 200,
                'result': func(),
                'msg': ''
            })

        return inner

    api_list = [

    ]

    for name, func in sql_api_map.items():
        wrap_func = res_wrap(func)
        path = f'/db/{name}'
        _ = app.route(path)(wrap_func)

        api_list.append(_create_url_link(name, path))

    prefs_api_map = get_prefs_api_map()
    for name, func in prefs_api_map.items():
        wrap_func = res_wrap(func)
        path = f'/pref/{name}'
        _ = app.route(path)(wrap_func)
        api_list.append(_create_url_link(name, path))

    app.route('/docs')(_doc_route(api_list))
    return app
