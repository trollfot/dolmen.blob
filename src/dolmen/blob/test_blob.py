# -*- coding: utf-8 -*-

import pytest
import transaction
import cStringIO
import zope.component

from cgi import FieldStorage
from BTrees.OOBTree import OOBTree
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage
from ZODB.interfaces import IBlobStorage, IBlob
from grokcore.component import testing
from persistent import Persistent
from zope.interface import Interface, implements, verify

from dolmen.blob import BlobFile, BlobValue, BlobProperty, IBlobFile
from dolmen.blob import IFileStorage, StorageError
from zope.filerepresentation.interfaces import IReadFile, IWriteFile
from cromlech.file import IFile, FileField
from dolmen.builtins import IDict


class IContent(Interface):
    binary = FileField(title=u"Binary data")


class MyContent(Persistent):
    implements(IContent)
    binary = BlobProperty(IContent['binary'])


class BlobStorage(object):

    def __init__(self):
        """Prepares for a functional test case.
        """
        transaction.abort()

        storage = DemoStorage("Demo Storage")

        if not IBlobStorage.providedBy(storage):
            raise RuntimeError

        self.db = DB(storage)
        self.connection = None

    def clean(self):
        """Cleans up after a functional test case.
        """
        transaction.abort()
        if self.connection:
            self.connection.close()
            self.connection = None
        self.db.close()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        self.db.close()

    def open(self):
        if self.connection:
            self.close()
        self.connection = self.db.open()
        return self.connection.root()


def setup_module(module):
    testing.grok("dolmen.blob")


def test_blob_file():
    """Test BlobFile instanciation.
    """
    blob = BlobFile()
    assert blob.content_type == 'application/octet-stream'
    assert blob.data == ''
    assert blob.filename == u''

    blob = BlobFile(data='mydata', filename="foo.txt")
    assert blob.filename == u'foo.txt'
    assert blob.data == 'mydata'
    assert blob.content_type == 'text/plain'

    blob = BlobFile(data=u'some random data', filename="foo.txt")
    assert blob.filename == u'foo.txt'
    assert blob.data == 'some random data'

    blob = BlobFile(content_type="plain/text")
    assert blob.filename == u''
    assert blob.data == ''
    assert blob.content_type == 'plain/text'

    data = cStringIO.StringIO("mydata")
    blob = BlobFile(data=data)
    assert blob.data == 'mydata'
    assert blob.size == 6

    reader = IReadFile(blob)
    writer = IWriteFile(blob)

    assert reader.read() == 'mydata'
    assert reader.size() == 6

    writer.write('changing data')
    assert reader.read() == 'changing data'
    assert reader.size() == 13

    blob = BlobFile(data='my data')
    assert verify.verifyObject(IBlobFile, blob)
    assert verify.verifyObject(IFile, blob)


def test_storage_error():
    """If the storage can't find a way to persist the data, a
    `dolmen.blob.StorageError` exception is raised.
    """
    with pytest.raises(StorageError) as e:
        blob = BlobFile(data={'something': 1})

    assert e.value.message == (
        "An error occured during the blob storage. Check the value "
        "type (<type 'dict'>). This value should implement IFile, "
        "IString or IUnicode (see `dolmen.builtins`).")

    def store_dict(blob, dictionnary):
        dict_repr = repr(dictionnary.items())
        fp = blob.open('w')
        fp.write(dict_repr)
        fp.close()
        return True

    zope.component.provideAdapter(
        store_dict, adapts=(IBlob, IDict), provides=IFileStorage)

    blob = BlobFile(data={'something': 1})
    assert blob.data == "[('something', 1)]"


def test_blob_copy():
    """`dolmen.blob` provides a blob to blob copy, using shutils.
    """
    source = BlobFile(data='Some data here')
    destination = BlobFile(data='')

    destination.data = source
    assert destination.data == 'Some data here'


def test_fs_access():
    """In some cases, it's useful to be able to be able to get the location
    of the physical blob file on the filesystem. This is possible through
    the attribute `physical_path`. However, this attribute is available
    only when the file has been persisted and the transaction commited.
    """
    db = BlobStorage()
    root = db.open()
    root['myblob'] = BlobFile(data='my data', filename="data.txt")

    myblob = root['myblob']
    assert myblob.physical_path is None

    transaction.commit()
    assert myblob.physical_path.endswith('.blob')


def test_blob_property():
    manfred = MyContent()
    manfred.binary = 'Foobar'
    assert manfred.binary.__class__ == BlobValue
    assert verify.verifyObject(IBlobFile, manfred.binary)


def test_copy_hooks():
    """A copy hook exists for IBlob objects. It allows to copy stored
    blobs transparently, while working with `zope.copy`.
    """
    import zope.copy

    source = BlobFile(data='Some data here')
    target = zope.copy.copy(source)
    assert target.data == 'Some data here'

    root = {}

    # It should works recursiverly
    root['gunther'] = OOBTree()
    root['gunther']['mammoth'] = MyContent()

    manfred = root['gunther']['mammoth']
    manfred.binary = 'Some data with no interest'
    manfred.binary.filename = u"filename.txt"
    manfred.binary.content_type = "text/plain"

    copy_of_gunther = zope.copy.copy(root['gunther'])
    judith = copy_of_gunther['mammoth']

    assert judith.binary.data == 'Some data with no interest'
    assert judith.binary.filename == u'filename.txt'
    assert judith.binary.content_type == 'text/plain'


boundary = "-----------------------------721837373350705526688164684"

POST = """--%(boundary)s
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

Testing 123.
--%(boundary)s--
""" % {'boundary': boundary}


def test_cgi_fieldstorage():

    env = {'REQUEST_METHOD': 'POST',
           'CONTENT_TYPE': 'multipart/form-data; boundary=%s' % boundary,
           'CONTENT_LENGTH': len(POST)}

    fs = FieldStorage(fp=cStringIO.StringIO(POST), environ=env)
    file = fs['file']
    
    blob = BlobFile(data=file)
    assert blob.data == 'Testing 123.'
