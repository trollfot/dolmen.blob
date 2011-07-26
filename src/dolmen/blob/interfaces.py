# -*- coding: utf-8 -*-

from dolmen.file import IFile
from zope.interface import Interface, Attribute


class IBlobFile(IFile):
    """A marker interface for file using ZODB blobs.
    """
    physical_path = Attribute("Physical path of the stored file.")


class IFileStorage(Interface):
    """A component dedicated to store items.
    """

    def __call__(file, data):
        """Persists the data in the file element.
        """
