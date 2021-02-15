from dataclasses import dataclass, field
import os
from .enum import fileds, itemTypes
from typing import Optional, List


@dataclass()
class Tag:
    tagId: int
    name: str
    type: Optional[int] = 0


@dataclass()
class ItemData():
    filed: fileds
    valueID: int
    value: str


@dataclass()
class Item():
    """
    one row
    """
    itemID: int = -1
    itemType: itemTypes = None
    key: str = None
    itemDatas: List[ItemData] = None


@dataclass()
class Collection:
    collectionID: int
    collectionName: str


@dataclass()
class Attachment:
    itemID: int
    key: str
    contentType: str
    relpath: str

    def abspath(self, root):
        return os.path.join(root, self.relpath)


@dataclass()
class Creator:
    creatorID: int = -1
    firstName: str = ""
    lastName: str = ""
    fieldMode: int = 0
