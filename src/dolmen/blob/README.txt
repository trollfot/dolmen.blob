===========
dolmen.blob
===========

`dolmen.blob` is a layer above `dolmen.file`, using the ZODB blobs as
a storage facility. It respects the `zope.app.file` IFile and the
`dolmen.file` INamedFile interfaces.


Compatibility
=============

In order to make sure that our BlobFile is functional, we test it
against some common uses, implemented by zope.app.file.file.File and
dolmen.file.NamedFile::

  >>> from dolmen.blob import BlobFile, IBlobFile

  >>> blob = BlobFile()
  >>> blob.contentType
  ''
  >>> blob.data
  ''
  >>> blob.filename
  u''

  >>> blob = BlobFile(data='mydata', filename="foo.txt")
  >>> blob.filename
  u'foo.txt'
  >>> blob.data
  'mydata'
  >>> blob.contentType
  'text/plain'

  >>> blob = BlobFile(data=u'some random data', filename="foo.txt")
  >>> blob.filename
  u'foo.txt'
  >>> blob.data
  'some random data'

  >>> import cStringIO
  >>> data = cStringIO.StringIO("mydata")
  >>> blob = BlobFile(data=data)
  >>> blob.data
  'mydata'
  >>> blob.getSize()
  6L


Let's verify the implementation in depth::

  >>> from dolmen.file import INamedFile
  >>> from zope.interface import verify
  >>> from zope.app.file.interfaces import IFile
  
  >>> blob = BlobFile(data='my data')
  >>> verify.verifyObject(IBlobFile, blob)
  True
  >>> verify.verifyObject(INamedFile, blob)
  True
  >>> verify.verifyObject(IFile, blob)
  True


Storage
=======

The ZODB blobs mimic a basic Python file and implement basic methods,
like read, write, readlines, seek, etc. In order to provide a very
pluggable and performant way to persist the datas, `dolmen.file`
proposes a storage mechanism, based on adapters. This idea, originally
implemented in z3c.blobfile, has been enhanced to rely on multi
adapters, adapting an ZODB.interfaces.IBlob and a data object.

As seen above, in the ``compatibility`` section, the
dolmen.blob.BlobFile handles String, Unicode and file-like objects,
out of the box.

Errors
------

If the storage can't find a way to persist the data, a
`dolmen.blob.StorageError` exception is raised::

  >>> blob = BlobFile(data={'something': 1})
  Traceback (most recent call last):
  ...
  StorageError: An error occured during the blob storage. Check the value type (<type 'dict'>). This value should implement IFile, IString or IUnicode (see `dolmen.builtins`).


Storage implementation
----------------------

The example above shows us that the Dict object is not handled by
dolmen.blob, out of the box. Let's implement a storage for this
usecase::

  >>> import zope.component
  >>> from ZODB.interfaces import IBlob
  >>> from dolmen.builtins import IDict
  >>> from dolmen.blob import IFileStorage
  
  >>> def store_dict(blob, dictionnary):
  ...     dict_repr = repr(dictionnary.items())
  ...     fp = blob.open('w')
  ...     fp.write(dict_repr)
  ...     fp.close()
  ...     return True

  >>> zope.component.provideAdapter(
  ...    store_dict, adapts=(IBlob, IDict), provides=IFileStorage)

  >>> blob = BlobFile(data={'something': 1})
  >>> blob.data
  "[('something', 1)]"


Accesses
========

Filesystem access
-----------------

In some cases, it's useful to be able to be able to get the location
of the physical blob file on the filesystem. This is possible through
the attribute `physical_path`. However, this attribute is available
only when the file has been persisted and the transaction commited::

  >>> import transaction
  >>> root = getRootFolder()
  >>> root['myblob'] = BlobFile(data='my data', filename="data.txt")

The transaction has not been commited, we try to access the attribute::

  >>> myblob = root['myblob']
  >>> print myblob.physical_path
  None
  
We now commit the transaction and retry::

  >>> transaction.commit()
  >>> print myblob.physical_path
  /tmp/tmp.../....blob


Browser access
--------------  

.. attention::

  Please read `dolmen.file` README.txt for more information.

As an dolmen.file.INamedFile, the BlobFile can bee accessed by the
browser, using a "file_publish" view::

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest

  >>> request = TestRequest()
  >>> view = getMultiAdapter((myblob, request), name='file_publish')
  >>> view
  <dolmen.file.access.FilePublisher object at ...>

  >>> view.update()
  >>> for key, value in view.response.getHeaders(): print key, repr(value)
  X-Powered-By 'Zope (www.zope.org), Python (www.python.org)'
  Content-Length '7'
  Content-Type 'text/plain'
  Content-Disposition 'attachment; filename="data.txt"'

  >>> view.render()
  'my data'


Property
========

.. attention::

  Please read `dolmen.file` README.txt for more information.

The persistency of the data can be handled, in complex object, by a
FileField using a BlobProperty::

  >>> from persistent import Persistent
  >>> from dolmen.file import FileField
  >>> from dolmen.blob import BlobProperty
  >>> from zope.interface import Interface, implements

  >>> class IContent(Interface):
  ...     binary = FileField(title=u"Binary data")

  >>> class MyContent(Persistent):
  ...     implements(IContent)
  ...     binary = BlobProperty(IContent['binary'])

  >>> root['mammoth'] = MyContent()
  >>> manfred = root['mammoth']
  >>> manfred.binary = 'Foobar'
  >>> manfred.binary
  <dolmen.blob.file.BlobFile object at ...>
