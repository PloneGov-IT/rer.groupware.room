from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from rer.groupware.room.interfaces import IGroupRoom


class GroupwareRoomViewletBase(ViewletBase):
    def __init__(self, context, request, view, manager):
        super(GroupwareRoomViewletBase, self).__init__(context, request, view, manager)
        self.room = self.getRoomObj()

    def render(self):
        if self.room:
            return self.index()
        else:
            return ""

    def getRoomObj(self):
        for elem in self.context.aq_inner.aq_chain:
            if IGroupRoom.providedBy(elem):
                return elem
        return None


class RERGroupwareRoomTitleViewlet(GroupwareRoomViewletBase):
    index = ViewPageTemplateFile('viewlets/groupware_room_title.pt')


class RERGroupwareRoomColorViewlet(GroupwareRoomViewletBase):
    """
    A Viewlet that allows to add some dynamic css in the  header
    """
    def render(self):
        import pdb; pdb.set_trace()
        if not self.room:
            return ""
#        color=self.room.getSubsiteColor()
        image = self.room.image
        return_string = ''
        # css = '#roomTitle {background-color:#552649'
        if image:
            url = '{0}/@@images/{1}/{2}'.format(self.context.absolute_url(), 'image', 'mini')
            css = '#roomTitle {background-image:url(%s); background-position: 100%% 0;}' % url
            return_string = "<style type='text/css'>%s</style>" % css
        return return_string
