from setuptools import setup, find_packages
import os

version = '0.5.0'

def description():
    join = lambda *paths: os.path.join('plone', 'app', 'z3cform', *paths)
    return (open('README.txt').read() + '\n' +
            open(join('wysiwyg', 'README.txt')).read() + '\n' +
            open(join('queryselect', 'README.txt')).read() + '\n' +
            open(os.path.join('docs', 'HISTORY.txt')).read() + '\n')

setup(name='plone.app.z3cform',
      version=version,
      description="A collection of widgets, templates and other components "
      "for use with z3c.form and Plone",
      long_description=description(),
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
          'Plone',
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
