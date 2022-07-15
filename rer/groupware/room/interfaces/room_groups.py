# -*- coding: utf-8 -*-
from plone.supermodel import model
from rer.groupware.room import roomMessageFactory as _
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import json

DEFAULT_ACTIVE_GROUPS = [
    {"group_id": "coordinators", "label": ["Coordinatori"]},
    {"group_id": "membersAdv", "label": ["Redattori"]},
    {"group_id": "members", "label": ["Collaboratori"]},
]

DEFAULT_PASSIVE_GROUPS = [{"group_id": "hosts", "label": ["Ospiti"]}]


class IRoomGroupName(model.Schema):
    group_id = schema.ASCIILine(title=_(u"Group ID"), required=True)
    label = schema.List(
        title=_("group_label", default=u"Label"),
        description=_(
            "group_label_help",
            default=u"Insert the label for this group. One per row. "
            u"If the site has only one language, type the simple name. "
            u"If it has multiple languages, insert one row per language in "
            u"the following format: lang|label. For example: it|Coordinatori",
        ),
        required=True,
        value_type=schema.TextLine(),
    )


class IRoomGroupsSettingsSchema(model.Schema):
    """Settings used in the control panel for set default room groups"""

    active_groups = schema.SourceText(
        title=_("Active room groups"),
        description=_(
            "help_active_groups",
            default="Insert a list of groups that are active in the rooms. This list will be used to generate some groups for every new room created.",
        ),
        required=False,
        default=json.dumps(DEFAULT_ACTIVE_GROUPS),
    )
    passive_groups = schema.SourceText(
        title=_("Passive room groups"),
        description=_(
            "help_passive_groups",
            default="Insert a list of passive groups. These groups can access to private rooms where they are enabled, but they can't do anything.",
        ),
        required=False,
        default=json.dumps(DEFAULT_PASSIVE_GROUPS),
    )
    collection_type = schema.Choice(
        title=_("Default collection type"),
        description=_("Select which collection type to use in this portal."),
        missing_value=set(),
        default="Collection",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("Collection", "Collection", _("Collection")),
                SimpleTerm("Topic", "Topic", _("Topic (old)")),
            ]
        ),
        required=False,
    )
