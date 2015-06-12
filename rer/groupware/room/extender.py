# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender, ISchemaExtender
from Products.Archetypes.atapi import LinesField, InAndOutWidget
from ftw.poodle.interfaces import IPoodle
from Products.Archetypes import PloneMessageFactory as _
from rer.groupware.room.interfaces import IRERGroupwareRoomLayer
from zope.component import adapts
from zope.interface import implements
from ftw.poodle import poodleMessageFactory as _


class PoodleLinesField(ExtensionField, LinesField):
    """Extension field for Poodle groups field"""


class GroupwarePoodleExtender(object):
    """
    Re-define groups field and use a custom default method for Poodle
    """
    adapts(IPoodle)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IRERGroupwareRoomLayer

    fields = [
      PoodleLinesField(
        'groups',
        accessor='getGroups',
        vocabulary_factory="rer.groupware.vocabularies.room_groups",
        enforceVocabulary=True,
        default_method='gpwDefaultPoodleGroups',
        widget=InAndOutWidget(
          label=_(u'ftwpoodle_label_groups', default=u'Groups'),
          actb_expand_onfocus=1),
        required=0,
        validators=('isPartecipantSet'),
        multiValued=1),
      PoodleLinesField(
        'users',
        accessor='getUsers',
        vocabulary_factory="ftw.poodle.users",
        enforceVocabulary=True,
        widget=InAndOutWidget(
          label=_(u'ftwpoodle_label_users', default=u'Users'),
          visible={'edit': 'invisible', 'view': 'invisible'},
          actb_expand_onfocus=1),
        required=0,
        validators=('isPartecipantSet'),
        multiValued=1),
      ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
