import os

from setuptools import find_packages, setup

version = '4.0.0.dev0'

setup(name='rer.groupware.room',
      version=version,
      description="rer.groupware.room",
      long_description=open("README.rst").read() + "\n" +
      open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      ],      
      keywords='plone plonegov groupware',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='https://github.com/PloneGov-IT/rer.groupware.room',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rer', 'rer.groupware'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          #'Products.PlonePopoll',
          'Products.SimpleGroupsManagement>=0.7.0',
          'collective.contentrules.mailtogroup',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
