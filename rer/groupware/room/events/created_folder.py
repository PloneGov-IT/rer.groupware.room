# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

def setParentFilteredTypes(obj,event):
    parent=obj.aq_parent
    if obj.portal_type == 'GroupRoom' or parent.portal_type == 'GroupRoom':
        return
    obj.setConstrainTypesMode(parent.getConstrainTypesMode())
    obj.setLocallyAllowedTypes(parent.getLocallyAllowedTypes())
    obj.setImmediatelyAddableTypes(parent.getImmediatelyAddableTypes())
            