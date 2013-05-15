# -*- coding: utf-8 -*-

from rer.groupware.room import logger


def uninstall(portal, reinstall=False):
    if not reinstall:
        # Don't want to delete all registry values if a Manager simply reinstall the product from ZMI
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-rer.groupware.room:uninstall')
        logger.info("Uninstall done")
