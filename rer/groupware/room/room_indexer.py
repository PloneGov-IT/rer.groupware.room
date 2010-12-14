from Products.ATContentTypes.interface.interfaces import IATContentType
from Products.ATContentTypes.interface.event import IATEvent
from plone.indexer import indexer

@indexer(IATContentType)
def parent_room_index(object, **kw):
    parent_folder=object.getFolderWhenPortalFactory()
    for parent in parent_folder.aq_chain:
        if parent.portal_type == 'GroupRoom':
            return parent.Title()
    return ''
