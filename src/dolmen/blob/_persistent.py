# -*- coding: utf-8 -*-

from ZODB.blob import Blob
from ZODB.interfaces import BlobError
from os.path import getsize
from dolmen.file import NamedFile
from zope.cachedescriptors.property import CachedProperty

R_CHUNK = 4092


class BlobFile(NamedFile):

    def __init__(self, data=None, contentType='', filename=u''):
        self._blob = Blob()
        NamedFile.__init__(self, data, contentType, filename)

    @CachedProperty
    def physical_path(self):
        try:
            filename = self._blob.committed()
        except BlobError:
            filename = self._blob.committed()
        return filename

    def __len__(self):
        file = self._blob.open('r')
        try:
            file.seek(0, 2)
            result = file.tell()
        finally:
            file.close()
        return result

    getSize = __len__

    def __str__(self):
        return self.data
 
    def get(self, name, default=None):
         getattr(self, name, default)

    def setData(self, value):
        blob = self._blob.open('w')
        data = value.read(R_CHUNK)
        while data:
            blob.write(data)
            data = value.read(R_CHUNK)
        blob.close()

    def getData(self):
        blob = self._blob.open('r')
        data = blob.read()
        blob.close()
        return data

    data = property(getData, setData)
