# -*- coding: utf-8 -*-
"""Definition of the DocumentsArea content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IDocumentsArea
from zope.interface import implements

class DocumentsArea(folder.ATFolder):
    """Folder for Documents area"""
    implements(IDocumentsArea)

    meta_type = "DocumentsArea"

registerATCT(DocumentsArea, PROJECTNAME)
