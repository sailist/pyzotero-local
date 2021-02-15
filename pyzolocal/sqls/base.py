import zlib
import shutil
import os
from sqlite3 import Connection
from ..prefs.common import dataDir
from sqlite3 import connect


def exec_fetchall(sql):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(sql)
    values = cursor.fetchall()

    return cursor, values


def pako_inflate(data):
    """
    see
        https://github.com/zotero/zotero/blob/2adf0e6d3cab50959f0307fa2d663a9c82ea60bc/chrome/content/zotero/xpcom/schema.js#L365
    and
        https://stackoverflow.com/questions/46351275/using-pako-deflate-with-python
    :param data:
    :return:
    """
    decompress = zlib.decompressobj(15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data


def create_conn() -> Connection:
    """
        try create sqlite connection
    :return:
    """
    data_dir = dataDir()
    sqlite_fn = os.path.join(data_dir, 'zotero.sqlite')
    shutil.copy(sqlite_fn, os.path.join(data_dir, 'zotero.wrap.sqlite.bak'))
    sqlite_fn = os.path.join(data_dir, 'zotero.wrap.sqlite.bak')

    assert os.path.exists(sqlite_fn)
    return connect(sqlite_fn)
