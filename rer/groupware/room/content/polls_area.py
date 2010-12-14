# -*- coding: utf-8 -*-
"""Definition of the Polls Area content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IPollsArea
from zope.interface import implements

class PollsArea(folder.ATFolder):
    """Folder for Room"""
    implements(IPollsArea)

    meta_type = "PollsArea"

registerATCT(PollsArea, PROJECTNAME)
