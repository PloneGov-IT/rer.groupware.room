# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility, queryUtility

from plone import api

from plone.registry.interfaces import IRegistry

from rer.groupware.room.interfaces.room_groups import IRoomGroupsSettingsSchema
from .default_room_events import BaseEventClass


def userRemovedFromGroup(event):
    """If a user is removed from a group (room) it has to be removed from the all the notification groups of that room."""

    group = event.object['group']
    user_id = event.object['user_id']

    active_groups = api.portal.get_registry_record('active_groups', interface=IRoomGroupsSettingsSchema)
    passive_groups = api.portal.get_registry_record('passive_groups', interface=IRoomGroupsSettingsSchema)

    def get_roles():
        """This function returns a list of active and passive roles.
        """
        roles = []
        for agroup in active_groups:
            roles.append(agroup.group_id)
        for pgroup in passive_groups:
            roles.append(pgroup.group_id)
        return roles

    group_id = group._id            # training.hosts
    room = group_id.split('.')[0]   # training
    role = group_id.split('.')[1]   # hosts

    # Remove the user from the notify groups only if it is in active_groups or passive_groups

    for agroup in active_groups:
        if agroup.group_id == role:
            userGroups = api.group.get_groups(username=user_id)
            FOUND = False
            roles = get_roles()
            for group in userGroups:
                splitted_group = group.id.split('.')
                if splitted_group[0] == room:
                    if splitted_group[-1] in roles:
                        FOUND = True

            if not FOUND:
                for group in userGroups:
                    splitted_group = group.id.split('.')
                    if splitted_group[-1] == 'notify' and splitted_group[0] == room:
                        api.group.remove_user(groupname=group.id, username=user_id)


    for pgroup in passive_groups:
        if pgroup.group_id == role:
            userGroups = api.group.get_groups(username=user_id)
            FOUND = False
            roles = get_roles()
            for group in userGroups:
                splitted_group = group.id.split('.')
                if splitted_group[0] == room:
                    if splitted_group[-1] in roles:
                        FOUND = True

            if not FOUND:
                for group in userGroups:
                    splitted_group = group.id.split('.')
                    if splitted_group[-1] == 'notify' and splitted_group[0] == room:
                        api.group.remove_user(groupname=group.id, username=user_id)
