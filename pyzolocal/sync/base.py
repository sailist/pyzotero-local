import zipfile
import os
from ..prefs.base import profile_root


def compress(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.ZIP_DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar, arcname)
    zf.close()


def decompress(zipfilename, unziptodir):
    if not os.path.exists(unziptodir):
        os.makedirs(unziptodir, exist_ok=True)

    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir): os.makedirs(ext_dir, exist_ok=True)
            # TODO verify before overwrite
            with open(ext_filename, 'wb') as outfile:
                outfile.write(zfobj.read(name))


def bundle(target_dir='./'):
    compress(profile_root(), os.path.join(target_dir, 'Profiles.zip'))


def dump(source_fn, target_fn):
    decompress(source_fn, target_fn)
