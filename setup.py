from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '4.0.0'

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
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
    python_requires=">=3.8",
    install_requires=[
        'plone.app.textfield>=1.3.6',
        'plone.app.widgets>=2.4.2',
        'plone.base',
        'plone.protect',
        'setuptools',
        'z3c.form >= 4.0',
        'z3c.formwidget.query',
        'zope.deprecation',
        'zope.globalrequest',
        'Zope',
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
