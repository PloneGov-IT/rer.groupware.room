# -*- coding: utf-8 -*-
"""Definition of the Group Room content type
"""
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import schemata, folder
from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes import atapi
from Products.validation import V_REQUIRED
from Products.validation.config import validation
from Products.validation.interfaces import ivalidator
from Products.validation.validators.SupplValidators import MaxSizeValidator
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.config import PROJECTNAME
from rer.groupware.room.interfaces import IGroupRoom
from zope.interface import implements

RERGroupRoomSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    
    atapi.ImageField('image',
               required=False,
               languageIndependent=True,
               storage = atapi.AnnotationStorage(migrate=True),
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
               widget = atapi.ImageWidget(
                        description = '',
                        label= _(u'label_image', default=u'Image'),
                        show_content_type = False,)),
))

RERGroupRoomSchema['title'].storage = atapi.AnnotationStorage()
RERGroupRoomSchema['description'].storage = atapi.AnnotationStorage()
schemata.finalizeATCTSchema(RERGroupRoomSchema, moveDiscussion=False)

class GroupRoom(folder.ATFolder):
    """Folder for Room"""
    implements(IGroupRoom)
    schema = RERGroupRoomSchema
    meta_type = "GroupRoom"
    
    def hasRoomImageIcon(self):
        """
        Check if the room has the listing miniature.
        This can be used for example in a custom navigator, to show the room icon and not the archetype icon
        """
        if self.getImage():
            img_view=self.restrictedTraverse('@@images',None)
            if img_view:
                 scale=img_view.scale('image',scale='listing')
                 if scale:
                     return True
        return False

registerATCT(GroupRoom, PROJECTNAME)
