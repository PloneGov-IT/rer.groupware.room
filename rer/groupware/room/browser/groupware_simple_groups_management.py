# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.SimpleGroupsManagement.browser.simple_groups_management import \
    SimpleGroupsManagement
from zope.event import notify
from AccessControl import Unauthorized
from Products.SimpleGroupsManagement.group_event import UserAddedToGroup, UserRemovedFromGroup


class GroupwareSimpleGroupsManagement(SimpleGroupsManagement):
    """Main view for manage groups od the Plone portal"""

    main_template = ViewPageTemplateFile("templates/groupware_simple_groups_management.pt")
    manage_group_template = ViewPageTemplateFile("templates/groupware_manage_group_template.pt")

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

    def load_group_members(self, group):
        """Load member from a group and sort by surname"""
        if group:
            users_list = group.getGroupMembers()
            users_list.sort(lambda x, y: cmp(x.getProperty('fullname', ''), y.getProperty('fullname', '')))
            return users_list
        return []

    def load_portalmembers(self):
        """Return all members of the portal"""
        pas_search = self.context.restrictedTraverse('@@pas_search')
        list_users = []
        if self.request.form.get('form.button.FindAll'):
            users = pas_search.searchUsers(sort_by='userid')
        elif self.request.form.get('form.button.Search') and self.request.form.get('searchstring'):
            users = pas_search.searchUsers(sort_by='userid',
                                         fullname=self.request.form.get('searchstring'),
                                         id=self.request.form.get('searchstring'),
                                         )
        else:
            return []
        for user in users:
            user_obj = self.acl_users.getUser(user.get('id', ''))
            if user_obj:
                user['fullname'] = user_obj.getProperty('fullname', '')
                list_users.append(user)
        return list_users

    def getSortedSearchMembers(self, members_list):
        """
        sort a list of members
        """
        if members_list:
            members_list.sort(lambda x, y: cmp(x.get('fullname', ''), y.get('fullname', '')))
        return members_list

    def delete(self):
        """Delete users from the group"""
        group_id = self.request.get("group_id")
        if group_id not in self.manageableGroupIds():
            raise Unauthorized()
        user_ids = self.request.get("user_id")
        group = self.acl_users.getGroup(group_id)
        for user_id in user_ids:
            group.removeMember(user_id)
            notify(UserRemovedFromGroup(group, user_id))
        self.request.response.redirect(self.context.absolute_url() + '/@@gpw_simple_groups_management?group_id=%s&deleted=1' % group_id)

    def add(self):
        """Add users from the group"""
        group_id = self.request.get("group_id")
        if group_id not in self.manageableGroupIds():
            raise Unauthorized()
        user_ids = self.request.get("user_id")
        group = self.acl_users.getGroup(group_id)
        for user_id in user_ids:
            group.addMember(user_id)
            notify(UserAddedToGroup(group, user_id))
        self.request.response.redirect(self.context.absolute_url() + '/@@gpw_simple_groups_management?group_id=%s&added=1' % group_id)
    