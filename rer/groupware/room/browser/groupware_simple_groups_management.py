# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.SimpleGroupsManagement.browser.simple_groups_management import \
    SimpleGroupsManagement
from zope.component import getAdapter


class GroupwareSimpleGroupsManagement(SimpleGroupsManagement):

    """Main view for manage groups od the Plone portal"""

    main_template = ViewPageTemplateFile(
        "templates/groupware_simple_groups_management.pt")

    @property
    def many_users(self):
        return getAdapter(
            aq_inner(self.context), IUserGroupsSettingsSchema).many_users

    def createGroupsDict(self):
        groups_list = self.manageable_groups()
        groups_dict = {}
        if groups_list:
            for group in groups_list:
                group_id = group.get('id', '')
                if not '.' in group_id:
                    group_dict_key = group_id
                    group_title = group.get('title', group_id)
                else:
                    room_id = group_id[:group_id.index('.')]
                    pc = getToolByName(self.context, 'portal_catalog')
                    group_room = pc(portal_type="GroupRoom", id=room_id)
                    if not group_room:
                        group_dict_key = room_id
                        group_title = room_id
                    else:
                        group_title = group_room[0].Title
                        group_dict_key = room_id
                if not group_dict_key in groups_dict:
                    groups_dict[group_dict_key] = {'title': group_title,
                                                   'list': [group]}
                else:
                    groups_dict[group_dict_key]['list'].append(group)
        return groups_dict
