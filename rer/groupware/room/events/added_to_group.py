# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

def setNotifyGroup(info_dict,event):
    if not info_dict['group'].getProperty('roomgroup'):
        return
    group_id="%s.notificheSmall" %info_dict['group'].getId()
    site_root=getSite()
    acl_users=getToolByName(site_root,'acl_users')
    group = acl_users.getGroup(group_id)
    if not group:
        return
    group.addMember(info_dict['user_id'])
    