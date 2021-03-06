# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.supermodel import model
# from rer.groupware.room import roomMessageFactory as _
# from zope import schema
from zope.interface import Interface


class IGroupRoom(Interface):

    """A Room for Groupware"""

    # forumModerated = schema.Bool(
    #     title=_(u"label_forummoderated", default=u"Forum moderated"),
    #     default=False,
    #     description=_(u"help_forummoderated", default=u"Select if having a moderated forum, or not. Default forum is open to all."),
    # )


class INewsAreaSchema(model.Schema):

    """ Schema for NewsArea """


class IDocumentsAreaSchema(model.Schema):

    """ Schema for DocumentsArea """


class IEventsAreaSchema(model.Schema):

    """ Schema for EventsArea """


class IPollsAreaSchema(model.Schema):

    """ Schema for PollsArea """
