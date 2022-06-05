import os

from setuptools import find_packages, setup

version = "3.0.1.dev0"

setup(
    name="rer.groupware.room",
    version=version,
    description="rer.groupware.room",
    long_description=open("README.rst").read()
    + "\n"
    + open(os.path.join("docs", "HISTORY.rst")).read(),
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone plonegov groupware",
    author="RedTurtle Technology",
    author_email="sviluppoplone@redturtle.it",
    url="https://github.com/PloneGov-IT/rer.groupware.room",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["rer", "rer.groupware"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.SimpleGroupsManagement>=0.7.0",
        "collective.contentrules.mailtogroup",
        "collective.z3cform.jsonwidget",
    ],
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
