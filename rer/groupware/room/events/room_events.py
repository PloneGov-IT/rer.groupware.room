from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import implementer


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


@implementer(IRoomCreatedEvent)
class RoomCreatedEvent(ObjectEvent):
    """First event fired when a room is created"""

    def __init__(self, object):
        super(RoomCreatedEvent, self).__init__(object)


@implementer(IRoomCreateAreasEvent)
class RoomCreateAreasEvent(ObjectEvent):
    """Event fired for create working areas"""

    def __init__(self, object):
        super(RoomCreateAreasEvent, self).__init__(object)


@implementer(IRoomCreateGroupsEvent)
class RoomCreateGroupsEvent(ObjectEvent):
    """Event fired for create groups"""

    def __init__(self, object):
        super(RoomCreateGroupsEvent, self).__init__(object)


@implementer(IRoomCreateRulesEvent)
class RoomCreateRulesEvent(ObjectEvent):
    """Event fired for create contentrules"""

    def __init__(self, object):
        super(RoomCreateRulesEvent, self).__init__(object)


@implementer(IRoomCreateHomePageEvent)
class RoomCreateHomePageEvent(ObjectEvent):
    """Event fired for create room homepage"""

    def __init__(self, object):
        super(RoomCreateHomePageEvent, self).__init__(object)


@implementer(IRoomCreateSharingEvent)
class RoomCreateSharingEvent(ObjectEvent):
    """Event fired for create sharing configurations for the room"""

    def __init__(self, object):
        super(RoomCreateSharingEvent, self).__init__(object)


@implementer(IRoomPostCreatedEvent)
class RoomPostCreatedEvent(ObjectEvent):
    """Event fired at the end of creation steps"""

    def __init__(self, object):
        super(RoomPostCreatedEvent, self).__init__(object)
