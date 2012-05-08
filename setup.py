import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.5.8'

long_description = (
    read('README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'wysiwyg', 'README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'queryselect', 'README.txt')
    + '\n' +
    read('plone', 'app', 'z3cform', 'kss', 'README.txt')
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
        "Topic :: Software Development :: Libraries :: Python Modules",
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

      # If in Zope 2, z3c.form or another Zope 3 package starts
      # pulling incompatible dependencies, use the "fake zope eggs"
      # feature of plone.recipe.zope2install.
      install_requires=[
          'Zope2',
          'zope.interface',
          'setuptools',
          'plone.z3cform>=0.5.11dev',
          'kss.core',
          'plone.app.kss',
          'z3c.formwidget.query',
          'zope.component',
          'collective.z3cform.datetimewidget>=0.1a2',
      ],
      extras_require = {
        'tests': ['collective.testcaselayer',]
      },
      )
