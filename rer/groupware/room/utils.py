# -*- coding: utf-8 -*-
from plone import api
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema

import json


def get_active_groups():
    active_groups = api.portal.get_registry_record(
        "active_groups", interface=IRoomGroupsSettingsSchema
    )
    if not active_groups:
        return []
    return format_data(data=active_groups)


def get_passive_groups():
    passive_groups = api.portal.get_registry_record(
        "passive_groups", interface=IRoomGroupsSettingsSchema
    )
    if not passive_groups:
        return []
    return format_data(data=passive_groups)


def format_data(data):
    groups = json.loads(data)
    for group in groups:
        title = _extract_label(group["label"])
        group["group_title"] = title
        del group["label"]
    return groups


def _extract_label(value):
    string_value = ""
    if len(value) == 1:
        return value[0]
    else:
        current_lang = api.portal.get_current_language()
        string_value = ""
        for option in value:
            lang, label = option.split("|")
            if lang and lang == current_lang:
                string_value = label
                break
    return string_value
