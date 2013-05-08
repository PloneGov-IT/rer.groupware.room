from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import implements


class IRoomCreatedEvent(IObjectEvent):
    """Marker interface for room that has been created"""


class IRoomCreateAreasEvent(IObjectEvent):
    """Marker interface for create areas"""


class IRoomCreateGroupsEvent(IObjectEvent):
    """Marker interface for create groups"""


class IRoomCreateRulesEvent(IObjectEvent):
    """Marker interface for create rules"""


class IRoomCreateHomePageEvent(IObjectEvent):
    """Marker interface for create homepage"""


class IRoomCreateSharingEvent(IObjectEvent):
    """Marker interface for create sharing"""


class IRoomPostCreatedEvent(IObjectEvent):
    """Marker interface for last step actions"""


class RoomCreatedEvent(ObjectEvent):
    """First event fired when a room is created"""
    implements(IRoomCreatedEvent)

    def __init__(self, object):
        super(RoomCreatedEvent, self).__init__(object)


class RoomCreateAreasEvent(ObjectEvent):
    """Event fired for create working areas"""
    implements(IRoomCreateAreasEvent)

    def __init__(self, object):
        super(RoomCreateAreasEvent, self).__init__(object)


class RoomCreateGroupsEvent(ObjectEvent):
    """Event fired for create groups"""
    implements(IRoomCreateGroupsEvent)

    def __init__(self, object):
        super(RoomCreateGroupsEvent, self).__init__(object)


class RoomCreateRulesEvent(ObjectEvent):
    """Event fired for create contentrules"""
    implements(IRoomCreateRulesEvent)

    def __init__(self, object):
        super(RoomCreateRulesEvent, self).__init__(object)


class RoomCreateHomePageEvent(ObjectEvent):
    """Event fired for create room homepage"""
    implements(IRoomCreateHomePageEvent)

    def __init__(self, object):
        super(RoomCreateHomePageEvent, self).__init__(object)


class RoomCreateSharingEvent(ObjectEvent):
    """Event fired for create sharing configurations for the room"""
    implements(IRoomCreateSharingEvent)

    def __init__(self, object):
        super(RoomCreateSharingEvent, self).__init__(object)


class RoomPostCreatedEvent(ObjectEvent):
    """Event fired at the end of creation steps"""
    implements(IRoomPostCreatedEvent)

    def __init__(self, object):
        super(RoomPostCreatedEvent, self).__init__(object)
