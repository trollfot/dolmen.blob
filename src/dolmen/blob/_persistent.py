# -*- coding: utf-8 -*-

from ZODB.blob import Blob
from os.path import getsize
from dolmen.file import NamedFile

R_CHUNK = 4092


class BlobFile(NamedFile):

    def __init__(self, data='', contentType='', filename=u''):
        self._blob = Blob()
        NamedFile.__init__(self, data, contentType, filename)

    def __len__(self):
        current_filename = self._blob._current_filename()
        if current_filename is None:
            return 0
        return getsize(current_filename)

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
