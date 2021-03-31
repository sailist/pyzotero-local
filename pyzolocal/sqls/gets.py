import os
import json
from ..sqls.base import exec_fetchall, pako_inflate
from typing import List, Dict
from ..beans.enum import fileds, itemTypes
from ..beans import types as t

from collections import defaultdict


def get_settings() -> dict:
    sql = """
    select value from settings
    """
    _, values = exec_fetchall(sql)

    return json.loads(pako_inflate(values[0][0]))

def get_creator(creatorID:int=-1) -> t.Creator:
    sql = f'select * from creators where creatorID={creatorID}'
    cursor, values = exec_fetchall(sql)
    return t.Creator(creatorID=i[0],firstName=i[1], lastName=i[2], fieldMode=i[3])


def get_creators() -> List[t.Creator]:
    sql = 'select creatorID from creators'
    cursor, values = exec_fetchall(sql)
    if len(values) > 0:
        return [get_creator(value[0]) for value in values]
    else:
        return []


def get_tags() -> List[t.Tag]:
    sql = 'select * from tags'
    cursor, values = exec_fetchall(sql)

    return [t.Tag(tagId=i[0], name=i[1])
            for i in values]


def get_collections() -> List[t.Collection]:
    sql = """
        select * from collections
    """

    cursor, values = exec_fetchall(sql)
    return [t.Collection(collectionID=i[0],
                         collectionName=i[1]) for i in values]


def get_itemids(include_delete=False) -> List[int]:
    if include_delete:
        sql = f"""
        select itemID from items
        """
    else:
        sql = f"""
        select itemID from items 
        where itemID not in (select itemID from deletedItems)
        """

    cursor, values = exec_fetchall(sql)
    return [i[0] for i in values]


def get_item_creators(itemID:int=-1) -> List[t.Creator]:
    if itemID == -1 : return []
    sql = f'select * from itemCreators where itemID={itemID}'
    cursor, values = exec_fetchall(sql)
    if len(values) > 0:
        return [get_creator(value[0]) for value in values]
    else:
        return []



def get_items_info() -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            left join itemDataValues  
        using (valueID)
    where itemID not in (select itemID from deletedItems)
    """

    cursor, values = exec_fetchall(sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    for item_id, val in item_value_map_.items():
        item_authors = get_item_creators(item_id)
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=get_item_key_by_itemid(item_id),
                      itemDatas=item_datas,
                      authors=item_authors)
        res.append(item)
    return res


def get_item_info_by_itemid(itemID: int) -> t.Item:
    sql = f"""
    select * from 
        (select * from itemData where itemID={itemID}) 
            inner join itemDataValues using (valueID)
    """

    cursor, values = exec_fetchall(sql)
    if len(values) == 0:
        return t.Item(-1)

    item_id = values[0][0]

    item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in values]
    item_authors = get_item_creators(item_id)
    return t.Item(itemID=item_id,
                  key=get_item_key_by_itemid(itemID),
                  itemDatas=item_datas,
                  authors=item_authors)


def get_attachments(type=-1) -> List[t.Attachment]:
    """
    all attached files
    :param conn:
    :return:
    """
    if type == -1:
        sql = """
            select itemID,key,contentType,path from (
                itemAttachments inner join items using (itemID)
            )
        """
    else:
        raise NotImplementedError()

    cursor, values = exec_fetchall(sql)

    res = []
    for (itemID, key, contentType, path) in values:
        if path is not None:
            relpath = os.path.join('storage', key, path.replace('storage:', ''))
        else:
            relpath = None
        file = t.Attachment(itemID=itemID, key=key,
                            contentType=contentType, relpath=relpath)
        res.append(file)
    return res


def get_attachments_by_parentid(parentItemID: int) -> List[t.Attachment]:
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

    cursor, values = exec_fetchall(sql)
    if len(values) == 0:
        return []

    item_value_map_ = {}
    for value in values:
        item_value_map_[value[0]] = value

    res = []
    # item_id_type_map = get_items_type_by_itemids(*list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(*list(item_value_map_.keys()))

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


def get_item_attachments_by_parentid(parentItemID: int) -> List[t.Item]:
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

    cursor, values = exec_fetchall(sql)
    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(*list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(*list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item_authors = get_item_creators(item_id)
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas,
                      authors=item_authors)
        res.append(item)
    return res


def get_items_info_from_tag_by_tagid(tagID: int) -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            inner join itemDataValues using (valueID)
            inner join (select itemID from itemTags where tagID={tagID}) using (itemID)
    """
    cursor, values = exec_fetchall(sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(*list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(*list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas)
        res.append(item)
    return res


def get_items_info_from_coll_by_collid(collID: int) -> List[t.Item]:
    sql = f"""
    select * from 
        (select * from itemData) 
            inner join itemDataValues using (valueID)
            inner join (select itemID from collectionItems where collectionID={collID}) using (itemID)
    """

    cursor, values = exec_fetchall(sql)

    if len(values) == 0:
        return []

    item_value_map_ = defaultdict(list)
    for value in values:
        item_value_map_[value[0]].append(value)

    res = []
    item_id_type_map = get_items_type_by_itemids(*list(item_value_map_.keys()))
    item_id_key_map = get_items_key_by_itemid(*list(item_value_map_.keys()))

    for item_id, val in item_value_map_.items():
        item_datas = [t.ItemData(fileds(i[1]), i[2], i[3]) for i in val]
        item_authors = get_item_creators(item_id)
        item = t.Item(itemID=item_id,
                      key=item_id_key_map[item_id],
                      itemType=itemTypes(item_id_type_map[item_id]),
                      itemDatas=item_datas,
                      authors=item_authors)
        res.append(item)
    return res


def get_items_key_by_itemid(*itemID: int) -> Dict[int, str]:
    itemID_ = ','.join(f'{i}' for i in itemID)
    sql = f"""
        select itemID,key from items where itemID in ({itemID_})
    """
    cursor, values = exec_fetchall(sql)

    items_type = {i[0]: i[1] for i in values}

    return items_type


def get_item_key_by_itemid(itemID: int) -> str:
    return get_items_key_by_itemid(itemID)[itemID]


def get_items_type_by_itemids(*itemID: int) -> Dict[int, itemTypes]:
    itemID_ = ','.join(f'{i}' for i in itemID)
    sql = f"""
        select itemID,itemTypeID from items where itemID in ({itemID_})
    """
    cursor, values = exec_fetchall(sql)

    items_type = {i[0]: itemTypes(i[0]) for i in values}

    return items_type


def get_item_type_by_itemid(itemID: int) -> itemTypes:
    return get_item_type_by_itemid(itemID)[0]


def get_item_tags_by_itemid(itemID: int) -> List[t.Tag]:
    sql = f"""
        select * from
        (select * from itemTags where itemID={itemID})
            inner join tags using (tagID) 
    """
    cursor, values = exec_fetchall(sql)
    return [t.Tag(i[0], i[1]) for i in values]
