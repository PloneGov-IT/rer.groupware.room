from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope import component
from zope.component.hooks import getSite
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


class AvailableRoomGroupsVocabulary(object):
    """
    lists all available groups for ftw.poodle
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        """If we are in a room, return only availabel room's groups.
        Otherwise returns all groups
        """
        if context is None:
            context = getSite()
        room_helper_view = context.restrictedTraverse("@@room_helper_view")
        room_groups = room_helper_view.getRoomGroupIds()
        if not room_groups:
            factory = component.getUtility(
                IVocabularyFactory,
                name='plone.app.vocabularies.Groups',
                context=context)
            return factory(context)
        return SimpleVocabulary([SimpleTerm(x[0], x[0], x[1]) for x in room_groups])

AvailableRoomGroupsVocabularyFactory = AvailableRoomGroupsVocabulary()
