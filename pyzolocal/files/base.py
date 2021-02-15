#!/usr/bin/env python3
import os
from itertools import chain
from ..prefs.common import dataDir

from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.query import *

import re


def index_root():
    root = os.path.join(dataDir(), 'index')
    if not os.path.exists(root):
        os.makedirs(root, exist_ok=True)
    return root


def storage_root():
    root = os.path.join(dataDir(), 'storage')
    return root


def hash_dir(*fs):
    from hashlib import md5
    hl = md5()
    for f in fs:
        hl.update(f.encode('utf-8'))
    for f in fs:
        hl.update(str(os.stat(f).st_atime + os.stat(f).st_mtime + os.stat(f).st_ctime).encode())
    return hl.hexdigest()


def index():
    schema = Schema(title=TEXT(stored=True, spelling_prefix=True),
                    itemID=NUMERIC(stored=True),
                    contentType=KEYWORD(stored=True),
                    key=ID(stored=True),
                    content=TEXT(stored=True, spelling_prefix=True), path=TEXT(stored=True))
    indexdir = index_root()
    datadir = dataDir()

    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
        ix = create_in(indexdir, schema)
    else:
        ix = open_dir(indexdir)

    writer = ix.writer()
    from ..sqls.base import create_conn
    from ..sqls.gets import get_attachments

    with create_conn() as conn:
        attachs = get_attachments(conn)

    for attach in attachs:
        _attach_f = os.path.join(datadir, attach.relpath)
        _attach_dir = os.path.dirname(_attach_f)
        _cache_f = os.path.join(_attach_dir, '.zotero-ft-cache')

        if not os.path.exists(_cache_f) or not os.path.exists(_attach_f):
            continue

        _dir_hash = hash_dir(_cache_f, _attach_f)
        _hash_cache_f = os.path.join(_attach_dir, '.cache')

        if os.path.exists(_hash_cache_f):
            with open(_hash_cache_f, 'r') as r:
                _old_hash = r.read().strip()
            if _dir_hash == _old_hash:
                continue
                pass

        with open(_hash_cache_f, 'w') as w:
            w.write(hash_dir(_cache_f, _attach_f))

        with open(_cache_f, 'r', encoding='utf-8', errors='ignore') as r:
            content = r.read()

        _pre, _ = os.path.splitext(os.path.basename(_attach_f))
        title = _pre.split(' - ')[-1]

        writer.add_document(title=title, content=content,
                            itemID=attach.itemID,
                            key=attach.key, path=attach.relpath)

    writer.commit()
    return ix.doc_count()
