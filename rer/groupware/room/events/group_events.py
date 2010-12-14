# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

def addNotifyGroup(info_dict,event):
    group_id=info_dict['group'].getId()
    user_id=info_dict['user_id']
    if not '.' in group_id:
        return
    site_root=getSite()
    acl_users=getToolByName(site_root,'acl_users')
    room_id = group_id[:group_id.index('.')]
    user=acl_users.getUser(user_id)
    group_notify_small="%s.notifySmall" %room_id
    group_notify_big="%s.notifyBig" %room_id
    user_groups=user.getGroups()
    already_signed=False
    for group in user_groups:
        if group.startswith(room_id) and not group == group_id:
            if group in [group_notify_small,group_notify_big]:
                already_signed = True
            else:
                group = acl_users.getGroup(group)
                group.removeMember(user_id)
    if already_signed:
        return
    group = acl_users.getGroup(group_notify_small)
    if not group:
        return
    group.addMember(user_id)

def removeNotifyGroup(info_dict,event):
    group_id=info_dict['group'].getId()
    if not '.' in group_id:
        return
    room_id = group_id[:group_id.index('.')]
    site_root=getSite()
    acl_users=getToolByName(site_root,'acl_users')
    notification_groups=["%s.notifySmall" %room_id,"%s.notifyBig" %room_id]
    for group_id in notification_groups: 
        group = acl_users.getGroup(group_id)
        if info_dict['user_id'] in group.getMemberIds():
            group.removeMember(info_dict['user_id'])
    
            