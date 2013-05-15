# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.custom_fields import IRoomGroupName, PersistentObject


class IRoomGroupsSettingsSchema(Interface):
    """Settings used in the control panel for set default room groups
    """
    room_groups = schema.Tuple(
            title=_(u'Room groups'),
            description=_('help_room_groups',
                          default=u"Insert a list of user groups. This list will be used to generate some groups for every new room created."),
            value_type=PersistentObject(IRoomGroupName, title=_(u"Group")),
            required=True,
            default=(),
            missing_value=(),
    )
