# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

from rer.groupware.room import logger

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
        if group:
            if info_dict['user_id'] in group.getMemberIds():
                group.removeMember(info_dict['user_id'])
                logger.info('Removed %s from %s' % (group_id, group.getId()))
        else:
            logger.warning("Can't find %s" % group_id)
