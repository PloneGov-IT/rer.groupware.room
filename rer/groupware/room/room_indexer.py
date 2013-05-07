from Products.Archetypes.interfaces import IBaseObject
from plone.indexer import indexer

@indexer(IBaseObject)
def parent_room_index(object, **kw):
    parent_folder=object.getFolderWhenPortalFactory()
    for parent in parent_folder.aq_chain:
        if getattr(parent,'portal_type','') == 'GroupRoom':
            return parent.Title()
    return ''
