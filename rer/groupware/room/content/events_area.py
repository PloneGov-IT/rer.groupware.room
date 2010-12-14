# -*- coding: utf-8 -*-
"""Definition of the Events Area content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IEventsArea
from zope.interface import implements

class EventsArea(folder.ATFolder):
    """Folder for events area"""
    implements(IEventsArea)

    meta_type = "EventsArea"

registerATCT(EventsArea, PROJECTNAME)
