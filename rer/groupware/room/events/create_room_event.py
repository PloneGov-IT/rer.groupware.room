# -*- coding: utf-8 -*-
from rer.groupware.room.events.room_events import RoomCreateAreasEvent,\
                                                  RoomCreatedEvent, \
                                                  RoomCreateGroupsEvent,\
                                                  RoomCreateHomePageEvent,\
                                                  RoomCreateRulesEvent,\
                                                  RoomCreateSharingEvent,\
                                                  RoomPostCreatedEvent
from zope.event import notify


def createRoomEvent(room, event):
    """
    This event throw some specified events for room initial setup
    """
    notify(RoomCreatedEvent(room))
    notify(RoomCreateAreasEvent(room))
    notify(RoomCreateGroupsEvent(room))
    notify(RoomCreateRulesEvent(room))
    notify(RoomCreateHomePageEvent(room))
    notify(RoomCreateSharingEvent(room))
    notify(RoomPostCreatedEvent(room))
