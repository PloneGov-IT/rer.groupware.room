# -*- coding: utf-8 -*-
from rer.groupware.room import logger

default_profile = 'profile-rer.groupware.room:default'


def to_2000(context):
    """
    Add e new registry field
    """
    logger.info('Upgrading rer.groupware.room to version 2000')
    context.runImportStepFromProfile(default_profile, 'plone.app.registry')
    logger.info('Reinstalled registry')
