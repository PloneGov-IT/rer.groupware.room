# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


def setRoomSharing(room, event):
    portal_state = getMultiAdapter((room, room.REQUEST), name=u'plone_portal_state')
    portal = portal_state.portal()
    pquickinstaller = getToolByName(portal, 'portal_quickinstaller')
    installed_products = pquickinstaller.listInstalledProducts()
    GPWRoomFound = False
    for p in installed_products:
        if p.get('id', '') == u'rer.groupware.room':
            GPWRoomFound = True
    if not GPWRoomFound:
        return
    wtool = getToolByName(portal, 'portal_workflow')
    review_state = wtool.getInfoFor(room, 'review_state')
    if review_state == 'published':
        room.manage_addLocalRoles('AuthenticatedUsers', ['Active User'])
    elif review_state == 'private':
        room.manage_delLocalRoles(['AuthenticatedUsers'])
        #reindex the security
        room.reindexObjectSecurity()
