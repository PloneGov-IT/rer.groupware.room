# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from ospfe.dimissioni.controlpanel.interfaces import IOspfeDimissioniSettings


class OspfeDimissioniSettingsEditForm(controlpanel.RegistryEditForm):
    """settings form."""
    schema = IOspfeDimissioniSettings
    id = "OspfeDimissioniSettingsEditForm"
    label = u"Configurazione Modulo Dimissioni"
    description = u""


class OspfeDimissioniSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """Analytics settings control panel.
    """
    form = OspfeDimissioniSettingsEditForm
