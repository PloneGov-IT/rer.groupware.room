import calendar
from DateTime import DateTime

#from zope.interface import implementer

from plone import api
# from collective.blog.view.interfaces import IBlogEntryRetriever
# from collective.blog.view.adapters import FolderEntryGetter
# from collective.blogstarentry.interfaces import IBlog
from Products.CMFCore.utils import getToolByName
from zope import component, interface

# @implementer(IBlogEntryRetriever)
# class GroupwareBlogEntryGetter(FolderEntryGetter):
#
#     """Gets blog entries in Blog type folder"""
#
#     
#     component.adapts(IBlog)
#
#     def __init__(self, context):
#         self.context = context
#
#     def _base_query(self):
#         portal_types = api.portal.get_registry_record(
#             'blog_types',
#             interface=IBlogEntryRetriever
#         )
#
#         if not portal_types:
#             portal_types = ('Document', 'News Item', 'File')
#
#         path = '/'.join(self.context.getPhysicalPath())
#
#         return dict(path={'query': path, 'depth': 1},
#                     portal_type=portal_types,
#                     sort_on='Date', sort_order='reverse')
#
#     def get_entries(self, year=None, month=None):
#         catalog = getToolByName(self.context, 'portal_catalog')
#         query = self._base_query()
#         if year:
#             if month:
#                 lastday = calendar.monthrange(year, month)[1]
#                 startdate = DateTime(year, month, 1, 0, 0)
#                 enddate = DateTime(year, month, lastday, 23, 59, 59)
#             else:
#                 startdate = DateTime(year, 1, 1, 0, 0)
#                 enddate = DateTime(year, 12, 31, 0, 0)
#             query['Date'] = dict(query=(startdate, enddate),
#                                  range='minmax')
#         return catalog.searchResults(**query)
