# -*- coding: utf-8 -*-
"""Definition of the News Area content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import INewsArea
from zope.interface import implements

class NewsArea(folder.ATFolder):
    """Folder for News Area"""
    implements(INewsArea)

    meta_type = "NewsArea"

registerATCT(NewsArea, PROJECTNAME)
