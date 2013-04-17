# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite


def removeNotifyGroup(info_dict, event):
    group_id = info_dict['group'].getId()
    if not '.' in group_id:
        return
    room_id = group_id[:group_id.index('.')]
    site_root = getSite()
    acl_users = getToolByName(site_root, 'acl_users')
    notification_groups = ["%s.notifyNewsEvents" % room_id, "%s.notifyDocs" % room_id]
    for group_id in notification_groups:
        group = acl_users.getGroup(group_id)
        if info_dict['user_id'] in group.getMemberIds():
            group.removeMember(info_dict['user_id'])
