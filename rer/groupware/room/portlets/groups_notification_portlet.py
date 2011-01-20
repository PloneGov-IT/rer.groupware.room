from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName

class IGroupsNotificationPortlet(IPortletDataProvider):
    """
    Portlet per visualizzare le news
    """
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IGroupsNotificationPortlet)

    @property
    def title(self):
        """
        Il titolo nel menu delle portlet
        """
        return "Group Notification Portlet" 


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view
        self.manager = manager
        self.data = data
        self.pg=getToolByName(self.context, 'portal_groups')
        self.pm=getToolByName(self.context,'portal_membership')
        if request.form.has_key('group_to_add') and request.form.get('room_id'):
            self.addUserToGroup(request.form.get('group_to_add'),request.form.get('room_id'))
            
    render = ViewPageTemplateFile('groups_notification_portlet.pt')
    
    @property
    def available(self):
        pm=getToolByName(self.context,'portal_membership')
        if pm.isAnonymousUser():
            return False
        if not self.listUserGroups():
            return False
        return True

    @memoize
    def listUserGroups(self):
        room=None
        for parent in self.context.aq_inner.aq_chain:
            if getattr(parent,'portal_type','') == 'GroupRoom':
                room=parent
        if not room:
            #i'm not in a room or subtree and the portlet will not be visible
            return {}
        room_id = room.getId()
        user=self.pm.getAuthenticatedMember()
        user_groups=user.getGroups()
        if not user_groups:
            return {}
        room_groups=[x for x in user_groups if x.startswith(room_id)]
        if not room_groups:
            return {}
        return {'title':room.Title(),
                'room_id':room_id,
                'notification_docs':'%s.notifyDocs'%room_id in user_groups,
                'notification_news_events':'%s.notifyNewsEvents'%room_id in user_groups}
    
    def addUserToGroup(self,group_id,room_id):
        group=self.pg.getGroupById('%s.%s' %(room_id,group_id))
        group_members=group.getMemberIds()
        userid=self.pm.getAuthenticatedMember().id
        if userid not in group_members:
            self.pg.addPrincipalToGroup(userid,'%s.%s' %(room_id,group_id))
        else:
            self.pg.removePrincipalFromGroup(userid,'%s.%s' %(room_id,group_id))
        return self.request.RESPONSE.redirect(self.context.absolute_url())
        
        
        
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
