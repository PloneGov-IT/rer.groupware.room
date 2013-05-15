# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface, implements
from z3c.form.object import registerFactoryAdapter
from plone.registry.field import PersistentField
from rer.groupware.room import roomMessageFactory as _


class IRoomGroupName(Interface):
    group_id = schema.ASCIILine(title=_(u"Group ID"), required=True)
    group_title = schema.TextLine(title=_(u"Group title"),
                                        required=False)


class RoomGroupName(object):
    implements(IRoomGroupName)


class PersistentObject(PersistentField, schema.Object):
    pass

registerFactoryAdapter(IRoomGroupName, RoomGroupName)
