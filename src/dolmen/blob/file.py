# -*- coding: utf-8 -*-

from os.path import getsize
from ZODB.blob import Blob
from ZODB.interfaces import BlobError
from dolmen.file import NamedFile
from dolmen.blob import IBlobFile, IFileStorage
from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.cachedescriptors.property import CachedProperty


class StorageError(Exception):
    """An error raised if the storage failed.
    """


class BlobFile(NamedFile):
    implements(IBlobFile)

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

    @apply
    def data():
        
        def set(self, value):
            stored = queryMultiAdapter((self._blob, value), IFileStorage)
            if stored is not True:
                raise StorageError

        def get(self):
            blob = self._blob.open('r')
            data = blob.read()
            blob.close()
            return data

        return property(get, set)
