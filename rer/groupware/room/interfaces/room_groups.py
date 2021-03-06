# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.custom_fields import IRoomGroupName, PersistentObject
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class IRoomGroupsSettingsSchema(Interface):
    """Settings used in the control panel for set default room groups
    """
    active_groups = schema.Tuple(
            title=_(u'Active room groups'),
            description=_('help_active_groups',
                          default=u"Insert a list of groups that are active in the rooms. This list will be used to generate some groups for every new room created."),
            value_type=PersistentObject(IRoomGroupName, title=_(u"Group")),
            required=False,
            default=(),
            missing_value=(),
    )
    passive_groups = schema.Tuple(
            title=_(u'Passive room groups'),
            description=_('help_passive_groups',
                          default=u"Insert a list of passive groups. These groups can access to private rooms where they are enabled, but they can't do anything."),
            value_type=PersistentObject(IRoomGroupName, title=_(u"Group")),
            required=False,
            default=(),
            missing_value=(),
    )
    collection_type = schema.Choice(
            title=_(u"Default collection type"),
            description=_(u"Select which collection type to use in this portal."),
            missing_value=set(),
            default="Collection",
            vocabulary=SimpleVocabulary([SimpleTerm('Collection', 'Collection', _(u"Collection")), SimpleTerm('Topic', 'Topic', _(u"Topic (old)"))]),
            required=False)
