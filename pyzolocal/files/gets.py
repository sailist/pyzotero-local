from .base import index_root
from itertools import chain

from whoosh.index import open_dir
from whoosh.query import *

import re

match_highlight = re.compile('<b class="match term([0-9]+)">([^<]+)<\/b>')

__all__ = ['search_content']




def search_content(*content: str, limit=10) -> dict:
    content = [i.lower() for i in content]
    ix = open_dir(index_root())
    searcher = ix.searcher()

    items = list(chain(*[i.split(' ') for i in content]))
    items = [Term('title', item) for item in items] + [Term('content', item) for item in items]

    quary = Or(items)

    results = searcher.search(q=quary, limit=limit)

    ress = []

    size = min(len(results), limit)
    for i in range(size):
        res = results[i].fields()
        path = res['path']
        title = results[i].highlights('title').split('...')[0]
        if len(title.strip()) == 0:
            title = res['title']
        results.fragmenter.surround = 75
        contents = results[i].highlights('content').replace('\n', ' ').split('...')

        ress.append({'title': title,
                     'path': path,
                     'contents': contents})

    return {
        'base': {
            'hit_count': size,
            'result_count': len(results),
            'doc_count': ix.doc_count()
        },
        'result': ress
    }
