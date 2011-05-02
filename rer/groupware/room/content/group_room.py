# -*- coding: utf-8 -*-
"""Definition of the Group Room content type
"""
from Products.ATContentTypes.content import schemata, folder
from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes import atapi
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IGroupRoom
from zope.interface import implements

from Products.validation.config import validation
from Products.validation.interfaces import ivalidator
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

RERGroupRoomSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    
    atapi.ImageField('image',
            widget=atapi.ImageWidget(
                label=_(u'rer_grouproom_image', default=u'Image'),
                description=_(u'rer_grouproom_image_help', default=u"Insert an image for the viewlet with the group name."),
            ),
            storage=atapi.AttributeStorage(),
            validators = (('isNonEmptyFile', V_REQUIRED)),
            ),
))

RERGroupRoomSchema['title'].storage = atapi.AnnotationStorage()
RERGroupRoomSchema['description'].storage = atapi.AnnotationStorage()
schemata.finalizeATCTSchema(RERGroupRoomSchema, moveDiscussion=False)

class GroupRoom(folder.ATFolder):
    """Folder for Room"""
    implements(IGroupRoom)
    schema = RERGroupRoomSchema
    meta_type = "GroupRoom"

registerATCT(GroupRoom, PROJECTNAME)
