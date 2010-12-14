# -*- coding: utf-8 -*-
"""Definition of the Projects Area content type
"""
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.base import registerATCT
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IProjectsArea
from zope.interface import implements

class ProjectsArea(folder.ATFolder):
    """Folder for ProjectsArea"""
    implements(IProjectsArea)

    meta_type = "ProjectsArea"

registerATCT(ProjectsArea, PROJECTNAME)
