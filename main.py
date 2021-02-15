from pyzolocal.sync.base import bundle, dump
from pyzolocal.apis.fastapi import get_fastapis

from pyzolocal.sqls.gets import get_item_key_by_itemid
from pyzolocal.sqls import create_conn
from functools import wraps

print(get_item_key_by_itemid.__annotations__)
print(get_item_key_by_itemid.__dict__)
# print(get_attachments.__doc__)
print(get_item_key_by_itemid.__closure__)
print(get_item_key_by_itemid.__defaults__)
print(get_item_key_by_itemid.__kwdefaults__)
# print(get_attachments.__)
# bundle('./')
# dump('./Profiles.zip',...)

from functools import partial

from types import FunctionType, CodeType


def conn_wrap(func):
    conn = create_conn()
    import inspect, importlib
    from types import ModuleType

    code = inspect.getsource(func)
    code_lis = code.split('\n')
    code_lis[0] = code_lis[0].replace('conn: Connection, ', '')
    code = '\n'.join(code_lis)

    exec(code, vars(module))

    return getattr(module, func.__name__)
