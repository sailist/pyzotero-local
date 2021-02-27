class Zotero():
    pass


api_list = """
see https://pyzotero.readthedocs.io/en/latest/

top
everything
key_info
count_items
publications
trash
deleted
item
children
collection_items
collection_items_top
get_subset


file
dump

collections
collections_top
collection
collections_sub
all_collections

tags
item_tags

item_versions
collection_versions

new_fulltext

fulltext_item

set_fulltext
follow
iterfollow
makeiter

The follow(), everything() and makeiter() methods are only valid for methods which can return multiple library items. For instance, you cannot use follow() after an item() call. The generator methods will raise a StopIteration error when all available items retrievable by your chosen API call have been exhausted.



num_items
num_collectionitems

last_modified_version
"""
