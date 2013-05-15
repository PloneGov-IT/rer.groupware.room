# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.custom_fields import RoomGroupName
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from zope.component import queryUtility
from zope.i18n import translate

DEFAULT_GROUPS = [('coordinators', 'Coordinators'),
                 ('membersAdv', 'Editors'),
                 ('members', 'Members'),
                 ('hosts', 'Hosts')]


def import_various(context):
    if context.readDataFile('groupwareroom-various.txt') is None:
        return
    # Define portal properties
    portal = context.getSite()
    updateSiteProperties(context, portal)
    addKeyToCatalog(context, portal)
    setDefaultGroups(portal)


def updateSiteProperties(context, portal):
    ptool = getToolByName(portal, 'portal_properties')
    props = getattr(ptool, 'site_properties', None)
    if not props:
        return
    types_not_searched = props.getProperty('types_not_searched')
    new_value = [x for x in types_not_searched if not x == 'PloneboardConversation']
    props.manage_changeProperties(types_not_searched=new_value)
    return


def addKeyToCatalog(context, portal):
    '''
    @summary: takes portal_catalog and adds a key to it
    @param context: context providing portal_catalog
    '''
    pc = portal.portal_catalog
    pl = portal.plone_log

    indexes = pc.indexes()
    for idx in getKeysToAdd():
        if idx[0] in indexes:
            pl("Found the '%s' index in the catalog, nothing changed.\n" % idx[0])
        else:
            pc.addIndex(name=idx[0], type=idx[1], extra=idx[2])
            pl("Added '%s' (%s) to the catalog.\n" % (idx[0], idx[1]))


def getKeysToAdd():
    '''
    @author: andrea cecchi
    @summary: returns a tuple of keys that should be added to portal_catalog
    '''
    return (('parentRoom', 'FieldIndex', {'indexed_attrs': 'parentRoom', }),)


def setDefaultGroups(portal):
    """
    insert some properties
    """
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
    if not settings.room_groups:
        room_groups = setRegistyField(portal, DEFAULT_GROUPS)
        settings.room_groups = room_groups


def setRegistyField(context, groups):
    """
    """
    groups_list = []
    for group in groups:
        group_id = group[0]
        group_title = translate(_(group[1]), context=context.REQUEST)
        new_value = RoomGroupName()
        new_value.group_id = group_id
        new_value.group_title = group_title
        groups_list.append(new_value)
    return tuple(groups_list)
