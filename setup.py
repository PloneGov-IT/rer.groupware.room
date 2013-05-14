from setuptools import setup, find_packages
import os

version = '1.3.3.dev0'

setup(name='rer.groupware.room',
      version=version,
      description="rer.groupware.room",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone plonegov groupware',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rer', 'rer.groupware'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PlonePopoll',
          'Products.Ploneboard>=3.4',
          'Products.SimpleGroupsManagement>=0.4.0',
          'redturtle.portlet.collection',
          'collective.contentrules.mailtogroup',
          'collective.portlet.discussion',
          'collective.portletpage',
          'collective.blogstarentry',
          'collective.portlet.blogstarentries',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
