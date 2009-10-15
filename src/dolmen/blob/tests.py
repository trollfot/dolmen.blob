import unittest

from zope.testing import doctest
from zope.app.testing import placelesssetup
from zope import component
    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            tearDown=placelesssetup.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
