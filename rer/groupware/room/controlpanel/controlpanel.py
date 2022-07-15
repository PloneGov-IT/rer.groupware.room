# -*- coding: utf-8 -*-
from collective.z3cform.jsonwidget.browser.widget import JSONFieldWidget
from plone.app.registry.browser import controlpanel
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.interfaces import IRoomGroupName
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from z3c.form import field
from Products.CMFPlone.resources import add_bundle_on_request


class RoomGroupsSettingsEditForm(controlpanel.RegistryEditForm):
    """Media settings form."""

    schema = IRoomGroupsSettingsSchema
    id = "RoomGroupsSettingsEditForm"
    label = _("Room groups settings")
    description = _("help_room_groups_editform", default="Manage default room groups")

    fields = field.Fields(IRoomGroupsSettingsSchema)
    fields["active_groups"].widgetFactory = JSONFieldWidget
    fields["passive_groups"].widgetFactory = JSONFieldWidget

    def updateWidgets(self):
        """
        Hide some fields
        """
        super(RoomGroupsSettingsEditForm, self).updateWidgets()
        self.widgets["active_groups"].schema = IRoomGroupName
        self.widgets["passive_groups"].schema = IRoomGroupName


class RoomGroupsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Analytics settings control panel."""

    def __call__(self):
        add_bundle_on_request(self.request, "z3cform-jsonwidget-bundle")
        return super().__call__()

    form = RoomGroupsSettingsEditForm
