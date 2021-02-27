"""
修复命名错误，删除多余的，报告缺失的
"""
import os
import shutil
from ..prefs.common import dataDir, KEY_STORAGE
from ..sqls import gets


def rename_like_file():
    for basename, (disdir, dir_like) in get_disappear().items():
        if len(dir_like) > 0:
            tgt = os.path.join(disdir, basename)
            src = os.path.join(disdir, dir_like[0])
            os.rename(src, tgt)
            print(src, 'to', tgt)


def delete_dir_not_in_db(rm=False):
    """
    :param rm: remove dir, if False, will only return dir list, or
        all directory(attachment) not in database will be deleted
    :return:

    see repair.db.insert_disappear_dir_in_db() for reverse operation
    """
    storage_root = os.path.join(dataDir(), KEY_STORAGE)
    storage_dirs = set(os.listdir(storage_root))
    db_keys = [attach.key for attach in gets.get_attachments()]

    res = []
    for key in storage_dirs:
        if not os.path.isdir(os.path.join(storage_root, key)):
            continue
        if key not in db_keys:
            res.append(os.path.join(storage_root, key))
    if rm:
        for dir in res:
            shutil.rmtree(dir)
    return res


def get_disappear():
    """
    获取 attachment 缺失的列表，疑似列表
    :return:
    """
    res = {}

    for attach in gets.get_attachments():
        if attach.is_attachment_url:
            continue

        if not os.path.exists(attach.abspath):
            disfn = os.path.basename(attach.abspath)

            disdir = os.path.dirname(attach.abspath)
            fnext = os.path.splitext(attach.abspath)[-1]

            if os.path.exists(disdir):
                dir_has = [i for i in os.listdir(disdir) if i.endswith(fnext)]
            else:
                dir_has = []

            res[disfn] = [
                disdir,
                dir_has
            ]
    return res
