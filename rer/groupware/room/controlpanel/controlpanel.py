# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.registry.browser import controlpanel
from z3c.form import button
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from rer.groupware.room import roomMessageFactory as _


class RoomGroupsSettingsEditForm(controlpanel.RegistryEditForm):
    """Media settings form.
    """
    schema = IRoomGroupsSettingsSchema
    id = "RoomGroupsSettingsEditForm"
    label = _("Room groups settings")
    description = _("help_room_groups_editform",
                    default="Manage default room groups")

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@room-groups-settings")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class RoomGroupsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Analytics settings control panel.
    """
    form = RoomGroupsSettingsEditForm
