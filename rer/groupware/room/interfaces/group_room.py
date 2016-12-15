# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope import schema
from rer.groupware.room import roomMessageFactory as _


class IGroupRoom(Interface):
    """A Room for Groupware"""

    forumModerated = schema.Bool(
        title=_(u"label_forummoderated", default=u"Forum moderated"),
        default=False,
        description=_(u"help_forummoderated", default=u"Select if having a moderated forum, or not. Default forum is open to all."),
    )
