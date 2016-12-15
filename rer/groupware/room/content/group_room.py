# -*- coding: utf-8 -*-
"""Definition of the Group Room content type
"""
from plone.dexterity.content import Container
from rer.groupware.room.interfaces.group_room import IGroupRoom
from zope.interface import implementer


@implementer(IGroupRoom)
class GroupRoom(Container):
    """Folder for Room"""

    def hasRoomImageIcon(self):
        """
        Check if the room has the listing miniature.
        This can be used for example in a custom navigator, to show the room icon and not the archetype icon
        """
        if self.getImage():
            img_view = self.restrictedTraverse('@@images', None)
            if img_view:
                scale = img_view.scale('image', scale='listing')
                if scale:
                    return True
        return False

    def getIconURL(self):
        """
        Get the absolute URL of the icon for the object.
        If there is a room icon, use his miniature.
        """
        if self.hasRoomImageIcon():
            return "%s/image_listing" % self.absolute_url()
        else:
            return super(GroupRoom, self).getIconURL()
