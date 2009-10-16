===========
dolmen.blob
===========

  >>> from grokcore.component import testing
  >>> testing.grok("dolmen.blob")

  >>> from dolmen.blob import BlobFile

  >>> blob = BlobFile(data='mydata', filename="foo.txt")
  >>> blob.filename
  u'foo.txt'
  >>> blob.data
  'mydata'

  >>> blob = BlobFile(data=u'some foreign data', filename="foo.txt")
  >>> blob.filename
  u'foo.txt'
  >>> blob.data
  'some foreign data'

  >>> import cStringIO
  >>> data = cStringIO.StringIO("mydata")
  >>> blob = BlobFile(data=data)
  >>> blob.data
  'mydata'
  >>> from dolmen.blob.interfaces import IFile
  >>> blob.getSize()
  6L

  >>> blob = BlobFile(data={'something': 1})
  Traceback (most recent call last):
  ...
  StorageError: An error occured during the blob storage. Check the value type (<type 'dict'>). This value should implement IFile, IString or IUnicode (see `dolmen.builtins`).
