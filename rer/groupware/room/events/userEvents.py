# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility, queryUtility
from default_room_events import BaseEventClass
from plone import api

from plone.registry.interfaces import IRegistry
from rer.groupware.room.interfaces.room_groups import IRoomGroupsSettingsSchema

def userRemovedFromGroup(event):
    """If a user is removed from a group (room) it has to be removed from the all the notification groups of that room."""

    group = event.object['group']
    user_id = event.object['user_id']

    registry = queryUtility(IRegistry)

    active_groups = api.portal.get_registry_record('active_groups', interface=IRoomGroupsSettingsSchema)
    passive_groups = api.portal.get_registry_record('passive_groups', interface=IRoomGroupsSettingsSchema)

    group_id = group._id            # training.hosts
    room = group_id.split('.')[0]   # training
    role = group_id.split('.')[1]   # hosts

    # Remove the user from the notify groups only if it is in active_groups or passive_groups

    for agroup in active_groups:
        if agroup.group_id == role:
            userGroup = api.group.get_groups(username=user_id)
            for elem in userGroup:
                splitted_group = elem.id.split('.')
                if splitted_group[-1] == 'notify' and splitted_group[0] == room:
                    api.group.remove_user(groupname=elem.id, username=user_id)


    for pgroup in passive_groups:
        if pgroup.group_id == role:
            userGroup = api.group.get_groups(username=user_id)
            for elem in userGroup:
                splitted_group = elem.id.split('.')
                if splitted_group[-1] == 'notify' and splitted_group[0] == room:
                    api.group.remove_user(groupname=elem.id, username=user_id)
