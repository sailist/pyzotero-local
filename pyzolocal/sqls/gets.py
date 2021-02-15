import os
import json
from ..sqls.base import exec_fetchall, pako_inflate
from typing import List, Dict
from sqlite3 import Connection
from ..beans.enum import fileds, itemTypes
from ..beans import types as t

from collections import defaultdict


def get_settings(conn: Connection) -> dict:
    sql = """
    select value from settings
    """
    _, values = exec_fetchall(conn, sql)

    return json.loads(pako_inflate(values[0]))


def get_creators(conn: Connection) -> List[t.Creator]:
    sql = 'select * from creators'
    cursor, values = exec_fetchall(conn, sql)
    return [t.Creator(creatorID=i[0],
                      firstName=i[1], lastName=i[2], fieldMode=i[3]) for i in values]


def get_tags(conn: Connection) -> List[t.Tag]:
    sql = 'select * from tags'
    cursor, values = exec_fetchall(conn, sql)

    return [t.Tag(tagId=i[0], name=i[1])
            for i in values]


def get_collections(conn: Connection) -> List[t.Collection]:
    sql = """
        select * from collections
    """

    cursor, values = exec_fetchall(conn, sql)
    return [t.Collection(collectionID=i[0],
                         collectionName=i[1]) for i in values]


def get_itemids(conn: Connection, include_delete=False) -> List[int]:
    if include_delete:
        sql = f"""
        select itemID from items
        """
    else:
        sql = f"""
        select itemID from items 
        where itemID not in (select itemID from deletedItems)
        """

    cursor, values = exec_fetchall(conn, sql)
    return [i[0] for i in values]


def get_items_info(conn: Connection) -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            left join itemDataValues  
        using (valueID)
    where itemID not in (select itemID from deletedItems)
    """

    cursor, values = exec_fetchall(conn, sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=get_item_key_by_itemid(conn, item_id),
                      itemDatas=item_datas)
        res.append(item)
    return res


def get_item_info_by_itemid(conn: Connection, itemID: int) -> t.Item:
    sql = f"""
    select * from 
        (select * from itemData where itemID={itemID}) 
            inner join itemDataValues using (valueID)
    """

    cursor, values = exec_fetchall(conn, sql)
    if len(values) == 0:
        return t.Item(-1)

    item_id = values[0][0]

    item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in values]
    return t.Item(itemID=item_id,
                  key=get_item_key_by_itemid(conn, itemID),
                  itemDatas=item_datas)


def get_attachments(conn: Connection) -> List[t.Attachment]:
    """
    all attached files
    :param conn:
    :return:
    """
    sql = """
        select itemID,key,contentType,path from (
            itemAttachments inner join items using (itemID)
        )
    """
    cursor, values = exec_fetchall(conn, sql)

    res = []
    for (itemID, key, contentType, path) in values:
        relpath = os.path.join('storage', key, path.replace('storage:', ''))
        file = t.Attachment(itemID=itemID, key=key,
                            contentType=contentType, relpath=relpath)
        res.append(file)
    return res


def get_attachments_by_parentid(conn: Connection, parentItemID: int) -> List[t.Attachment]:
    """
    get attached file from parent
    :param conn:
    :param parentItemID:
    :return:
    """
    sql = f"""
    select itemID,contentType,path from itemAttachments
    where itemID in (select itemID from itemAttachments where parentItemID={parentItemID})
    """

    cursor, values = exec_fetchall(conn, sql)
    if len(values) == 0:
        return []

    item_value_map_ = {}
    for value in values:
        item_value_map_[value[0]] = value

    res = []
    # item_id_type_map = get_items_type_by_itemids(conn, *list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(conn, *list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        path = val[2]  # type:str
        key = item_id_key_map[item_id]
        relpath = os.path.join('storage', key, path.replace('storage:', ''))
        item = t.Attachment(itemID=item_id,
                            key=key,
                            contentType=val[1],
                            relpath=relpath)
        res.append(item)
    return res


def get_item_attachments_by_parentid(conn: Connection, parentItemID: int) -> List[t.Item]:
    """
    get attached item from parent
    :param conn:
    :param parentItemID:
    :return:
    """
    sql = f"""
    select * from 
        (select * from itemData) 
            inner join itemDataValues  
        using (valueID)
    where itemID in (select itemID from itemAttachments where parentItemID={parentItemID})
    """

    cursor, values = exec_fetchall(conn, sql)
    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(conn, *list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(conn, *list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas)
        res.append(item)
    return res


def get_items_info_from_tag_by_tagid(conn: Connection, tagID: int) -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            inner join itemDataValues using (valueID)
            inner join (select itemID from itemTags where tagID={tagID}) using (itemID)
    """
    cursor, values = exec_fetchall(conn, sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(conn, *list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(conn, *list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas)
        res.append(item)
    return res


def get_items_info_from_coll_by_collid(conn: Connection, collID: int) -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            inner join itemDataValues using (valueID)
            inner join (select itemID from collectionItems where collectionID={collID}) using (itemID)
    """

    cursor, values = exec_fetchall(conn, sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(conn, *list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(conn, *list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas)
        res.append(item)
    return res


def get_items_key_by_itemid(conn: Connection, *itemID: int) -> Dict[int, str]:
    itemID_ = ','.join(f'{i}' for i in itemID)
    sql = f"""
        select itemID,key from items where itemID in ({itemID_})
    """
    cursor, values = exec_fetchall(conn, sql)

    items_type = {i[0]: i[1] for i in values}

    return items_type


def get_item_key_by_itemid(conn: Connection, itemID: int) -> str:
    return get_items_key_by_itemid(conn, itemID)[itemID]


def get_items_type_by_itemids(conn: Connection, *itemID: int) -> Dict[int, itemTypes]:
    itemID_ = ','.join(f'{i}' for i in itemID)
    sql = f"""
        select itemID,itemTypeID from items where itemID in ({itemID_})
    """
    cursor, values = exec_fetchall(conn, sql)

    items_type = {i[0]: itemTypes(i[0]) for i in values}

    return items_type


def get_item_type_by_itemid(conn: Connection, itemID: int) -> itemTypes:
    return get_item_type_by_itemid(conn, itemID)[0]


def get_item_tags_by_itemid(conn: Connection, itemID: int) -> List[t.Tag]:
    sql = f"""
        select * from
        (select * from itemTags where itemID={itemID})
            inner join tags using (tagID) 
    """
    cursor, values = exec_fetchall(conn, sql)
    return [t.Tag(i[0], i[1]) for i in values]
