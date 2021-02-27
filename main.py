import pyzolocal.repair
from pyzolocal.sync.base import bundle, dump
from pyzolocal.apis.fastapi import get_fastapis
from pyzolocal.apis.flask import get_flaskapis

from pyzolocal.sqls.gets import get_item_key_by_itemid
# from pyzolocal.sqls import create_conn
# from functools import wraps
#
# print(get_item_key_by_itemid.__annotations__)
# print(get_item_key_by_itemid.__dict__)
# # print(get_attachments.__doc__)
# print(get_item_key_by_itemid.__closure__)
# print(get_item_key_by_itemid.__defaults__)
# print(get_item_key_by_itemid.__kwdefaults__)
# # print(get_attachments.__)
# # bundle('./')
# # dump('./Profiles.zip',...)
#
# from functools import partial
#
# from types import FunctionType, CodeType
#
#
#
# app = get_flaskapis()
#
# app.run()
from pprint import pprint
from pyzolocal import repair
import os
for fn in repair.delete_dir_not_in_db():
    print(os.listdir(fn))

print()
# pprint(pyzolocal.repair.get_disappear())

import pyzotero

from pyzotero import zotero