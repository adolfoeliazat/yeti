import hashlib

from core.analytics import InlineAnalytics
from core.database import Link
from core.observables import Hash

HASH_TYPES_DICT = {'md5': hashlib.md5,
                   'sha1': hashlib.sha1,
                   'sha256': hashlib.sha256,
                   'sha512': hashlib.sha512}


class HashFile(InlineAnalytics):

    default_values = {
        "name": "HashFile",
        "description": "Extracts MD5, SHA1, SHA256, SHA512 hashes from file",
    }

    ACTS_ON = 'File'

    @staticmethod
    def each(f):
        try:
            l = f.body.length
        except AttributeError as e:  # File item has no content
            l = 0
        if l > 0:
            for h in HashFile.extract_hashes(f):
                h = Hash.get_or_create(value=h.hexdigest()).save()
                h.add_source("analytics")
                Link.connect(f, h)

    @staticmethod
    def extract_hashes(f):
        hashes = []
        f = f.body
        hashers = {k: HASH_TYPES_DICT[k]() for k in HASH_TYPES_DICT}

        while True:
            chunk = f.read(512*16)
            if not chunk:
                break
            for h in hashers.itervalues():
                h.update(chunk)

        return hashers.values()
