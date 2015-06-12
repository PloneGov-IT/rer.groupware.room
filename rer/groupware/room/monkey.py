# -*- coding: utf-8 -*-


def gpwDefaultPoodleGroups(self):
    """Retrieve the default groups to set in a new poodle"""
    room_helper_view = self.restrictedTraverse("@@room_helper_view")
    room_groups = room_helper_view.getRoomGroupIds(only_active=True)
    if not room_groups:
        return []
    return [x[0] for x in room_groups]
