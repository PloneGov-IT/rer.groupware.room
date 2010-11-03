# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

def addNotifyGroup(info_dict,event):
    if not info_dict['group'].getProperty('roomgroup'):
        return
    group_id="%s.notificheSmall" %info_dict['group'].getId()
    site_root=getSite()
    acl_users=getToolByName(site_root,'acl_users')
    group = acl_users.getGroup(group_id)
    if not group:
        return
    group.addMember(info_dict['user_id'])

def removeNotifyGroup(info_dict,event):
    if not info_dict['group'].getProperty('roomgroup'):
        return
    group_id=info_dict['group'].getId()
    site_root=getSite()
    acl_users=getToolByName(site_root,'acl_users')
    notification_groups=["%s.notificheSmall" %group_id,"%s.notificheBig" %group_id]
    for group_id in notification_groups: 
        group = acl_users.getGroup(group_id)
        if info_dict['user_id'] in group.getMemberIds():
            group.removeMember(info_dict['user_id'])
    
            