# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory
from logging import getLogger


roomMessageFactory = MessageFactory('rer.groupware.room')
logger = getLogger("rer.groupware.room")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
