# -*- coding: utf-8 -*-

import StringIO
from dolmen.file import INamedFile
from zope.publisher.browser import FileUpload
from zope.interface import Interface, Attribute, classImplements


class IBlobFile(INamedFile):
    """A marker interface for file using ZODB blobs.
    """
    physical_path = Attribute("Physical path of the stored file.")
    

class IFileStorage(Interface):
    """A component dedicated to store items.
    """
    def __call__(file, data):
        """Persists the data in the file element.
        """


class IFile(Interface):
    """Defines an python file builtin.
    """
    def seek(offset, whence=0):
        """Set the file's current position.
        """

    def read(size):
        """Read at most size bytes from the file.
        """

    def readline(length=None):
        """Read one entire line from the file.
        """

    def readlines(sizehint=0):
        """Read until EOF using readline() and return a list
        containing the lines thus read.
        """

    def write(s):
        """Write a string to the file.
        """

    def writelines(iterable):
        """Write a sequence of strings to the file.
        """

    def tell():
        """Return the file's current position.
        """

    def truncate(size=None):
        """Truncate the file's size.
        """
classImplements(file, IFile)
classImplements(StringIO.StringIO, IFile)

class IFileUpload(IFile):
    """Defines an Upload object created by zope.publisher
    for data elements in forms.
    """
classImplements(FileUpload, IFileUpload)
