from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '4.0.0.dev0'

long_description = (
    read('README.rst') +
    '\n' +
    read('plone', 'app', 'z3cform', 'wysiwyg', 'README.rst') +
    '\n' +
    read('plone', 'app', 'z3cform', 'inline_validation.rst') +
    '\n' +
    read('CHANGES.rst') +
    '\n'
)

setup(
    name='plone.app.z3cform',
    version=version,
    description="A collection of widgets, templates and other components "
                "for use with z3c.form and Plone",
    long_description=long_description,
    classifiers=[
        'Development Status :: 6 - Mature',
        "Framework :: Plone",
        "Framework :: Plone :: Core",
        "Framework :: Plone :: 5.2",
        "Framework :: Zope :: 4",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords='zope plone form widget template',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.app.z3cform',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Acquisition',
        'plone.app.textfield',
        'plone.app.widgets>=2.4.2.dev0',
        'plone.protect',
        'plone.z3cform>=0.5.11dev',
        'Products.CMFCore',
        'Products.CMFPlone',
        'setuptools',
        'six',
        'z3c.form >= 3.0',
        'z3c.formwidget.query',
        'zope.browserpage',
        'zope.component',
        'zope.deprecation',
        'zope.globalrequest',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
        'Zope2',
    ],
    extras_require={
        'tests': [
            'mock',
            'plone.app.robotframework',
            'plone.app.testing',
            'plone.browserlayer',
            'plone.testing',
            'zope.contentprovider',
            'zope.publisher',
            'zope.testing',
        ]
    },
)
