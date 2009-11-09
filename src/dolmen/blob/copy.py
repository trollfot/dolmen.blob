# -*- coding: utf-8 -*-

import grokcore.component as grok

from ZODB.blob import Blob
from dolmen.blob import IBlobFile
from zope.copy.interfaces import ICopyHook, ResumeCopy


class BlobFileCopyHook(grok.Adapter):
    """A copy hook for IBlobFile objects.
    """
    grok.implements(ICopyHook)
    grok.context(IBlobFile)

    def __call__(self, toplevel, register):
        register(self._copyBlob)
        raise ResumeCopy

    def _copyBlob(self, translate):
        target = translate(self.context)
        target._blob = Blob()
        target.data = self.context
