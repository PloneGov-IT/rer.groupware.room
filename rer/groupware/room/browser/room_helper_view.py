# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from zope.component import queryUtility


class RoomHelperView(BrowserView):
    """
    """

    @view.memoize
    def getRoom(self):
        """
        return the parent room in the actual context.
        """
        for parent in self.context.aq_inner.aq_chain:
            if getattr(parent, 'portal_type', '') == 'GroupRoom':
                return parent

    def getDefaultRoomGroups(self, only_active=False):
        """
        return the list of active and passive groups set in the portal
        control_panel
        """
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(
            IRoomGroupsSettingsSchema,
            check=False)
        active_groups = getattr(groups_settings, 'active_groups', None)
        passive_groups = getattr(groups_settings, 'passive_groups', None)
        if only_active:
            return active_groups
        return active_groups + passive_groups

    def getRoomGroupIds(self, only_active=False):
        room = self.getRoom()
        if not room:
            #we are not in a room
            return []
        default_groups = self.getDefaultRoomGroups(only_active)
        groups = []
        for group_type in default_groups:
            default_group_id = group_type.group_id
            default_group_title = group_type.group_title
            group_id = "%s.%s" % (room.getId(), default_group_id)
            group_title = "%s %s" % (room.Title(), default_group_title)
            groups.append((group_id, group_title))
        return groups
