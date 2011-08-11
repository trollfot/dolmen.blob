# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.blob'
version = '2.0a2'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3 >= 3.9.0',
    'cromlech.file',
    'dolmen.builtins >= 0.3.1',
    'dolmen.file >= 2.0a1',
    'grokcore.component',
    'setuptools',
    'zope.component',
    'zope.contenttype',
    'zope.copy',
    'zope.filerepresentation',
    'zope.interface',
    'zope.location',
    'zope.schema',
    ]

tests_require = [
    'pytest',
    'transaction',
    ]

setup(name=name,
      version=version,
      description='Dolmen zodb blob handlers',
      long_description=readme + '\n\n' + history,
      keywords='Grok Cromlech CMS Dolmen',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['dolmen'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      classifiers=[
          'Environment :: Web Environment',
          'Programming Language :: Python',
          ],
      )
