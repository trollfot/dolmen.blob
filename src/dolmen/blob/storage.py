# -*- coding: utf-8 -*-

import grokcore.component as grok
from ZODB.interfaces import IBlob
from zope.interface import Interface
from dolmen.builtins import interfaces as base
from dolmen.blob import IFileUpload, IFileStorage

CHUNK = 1 << 12


@grok.implementer(IFileStorage)
@grok.adapter(IBlob, base.IString)
def string_blob(blob, data):
    fp = blob.open('w')
    fp.write(data)
    fp.close()
    return True


@grok.implementer(IFileStorage)
@grok.adapter(IBlob, base.IUnicode)
def unicode_blob(blob, data):
    data = data.encode('UTF-8')
    string_blob(blob, data)
    return True


@grok.implementer(IFileStorage)
@grok.adapter(IBlob, Interface)
def filetype_blob(blob, data):
    try:
        data.seek(0)
        fp = blob.open('w')
        block = data.read(CHUNK)
        while block:
            fp.write(block)
            block = data.read(CHUNK)
        fp.close()
    except AttributeError:
        return False
    return True