from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "4.7.5"

long_description = (
    f"{Path('README.rst').read_text()}\n"
    f"{(Path('plone') / 'app' / 'z3cform' / 'inline_validation.rst').read_text()}\n"
    f"{Path('CHANGES.rst').read_text()}"
)

test_requirements = [
    "plone.app.contenttypes[test]",
    "plone.app.testing",
    "plone.autoform",
    "plone.browserlayer",
    "plone.dexterity",
    "plone.supermodel",
    "plone.testing",
    "zope.annotation",
    "zope.intid",
    "zope.publisher",
]

setup(
    name="plone.app.z3cform",
    version=version,
    description="A collection of widgets, templates and other components "
    "for use with z3c.form and Plone",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
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
    keywords="zope plone form widget template",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.z3cform",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "plone.app.textfield>=1.3.6",
        "plone.base",
        "plone.app.contentlisting",
        "plone.formwidget.namedfile>=3.1.0",
        "plone.i18n",
        "plone.protect",
        "plone.registry",
        "plone.schema",
        "plone.uuid",
        "plone.z3cform",
        "Products.GenericSetup",
        "pytz",
        "setuptools",
        "z3c.form >= 5.1",
        "z3c.relationfield",
        "zope.deprecation",
        "zope.globalrequest",
        "Zope",
    ],
    extras_require={
        # Until plone.app.z3cform 4.0.2 we only had the 'tests' extra.
        # In 4.0.3 we introduced the 'test' extra.
        # Keep 'tests' for backwards compatibility.
        # Remove it in Plone 7.
        "test": test_requirements,
        "tests": test_requirements,
    },
)
