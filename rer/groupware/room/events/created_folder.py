# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName


def setParentFilteredTypes(obj, event):
    parent = obj.aq_parent
    portal = obj.portal_url.getPortalObject()
    pquickinstaller = getToolByName(portal, 'portal_quickinstaller')
    installed_products = pquickinstaller.listInstalledProducts()
    GPWRoomFound = False
    for product in installed_products:
        if product['title'] == u'RER Groupware: Room':
            GPWRoomFound = True
            break
    if not GPWRoomFound:
        return
    if obj.portal_type == 'GroupRoom' or parent.portal_type in ['GroupRoom', 'Plone Site']:
        return
    obj.setConstrainTypesMode(parent.getConstrainTypesMode())
    obj.setLocallyAllowedTypes(parent.getLocallyAllowedTypes())
    obj.setImmediatelyAddableTypes(parent.getImmediatelyAddableTypes())
