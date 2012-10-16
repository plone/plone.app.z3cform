import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.7.0'

long_description = (
    read('README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'wysiwyg', 'README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'queryselect', 'README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'inline_validation.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='plone.app.z3cform',
      version=version,
      description="A collection of widgets, templates and other components "
      "for use with z3c.form and Plone",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        ],
      keywords='zope plone form widget template',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.z3cform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.z3cform.datetimewidget>=0.1a2',
          'plone.z3cform>=0.5.11dev',
          'z3c.formwidget.query',
          'Zope2',
          'zope.browserpage',
          'zope.component',
          'zope.interface',
          'zope.traversing',
      ],
      extras_require={
        'tests': ['collective.testcaselayer']
      },
      )
