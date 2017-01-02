import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.3'

long_description = (
    read('README.rst')
    + '\n' +
    read('plone', 'app', 'z3cform', 'wysiwyg', 'README.rst')
    + '\n' +
    read('plone', 'app', 'z3cform', 'queryselect', 'README.rst')
    + '\n' +
    read('plone', 'app', 'z3cform', 'inline_validation.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
    )

setup(
    name='plone.app.z3cform',
    version=version,
    description="A collection of widgets, templates and other components "
                "for use with z3c.form and Plone",
    long_description=long_description,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='zope plone form widget template',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.app.z3cform',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Acquisition',
        'Products.CMFCore',
        'Products.CMFPlone',
        'Zope2',  # Products.Five
        'plone.app.widgets>=2.0.0.dev0',
        'plone.protect',
        'plone.z3cform>=0.5.11dev',
        'z3c.form >= 3.0',
        'z3c.formwidget.query',
        'zope.browserpage',
        'zope.component',
        'zope.globalrequest',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
        'plone.app.textfield'
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
