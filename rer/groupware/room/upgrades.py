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


def to_2100(context):
    """
    Install ftw.poodle
    """
    logger.info('Installing ftw.poodle')
    context.runAllImportStepsFromProfile('profile-ftw.poodle:default')
    context.runImportStepFromProfile(default_profile, 'factorytool')
    context.runImportStepFromProfile(default_profile, 'workflow')
    context.runImportStepFromProfile(default_profile, 'typeinfo', run_dependencies=True)
    logger.info('Installed ftw.poodle')
