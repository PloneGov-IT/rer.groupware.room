# -*- coding: utf-8 -*-
"""Definition of the Group Room content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IGroupRoom
from zope.interface import implements

class GroupRoom(folder.ATFolder):
    """Folder for Room"""
    implements(IGroupRoom)

    meta_type = "GroupRoom"

registerATCT(GroupRoom, PROJECTNAME)
