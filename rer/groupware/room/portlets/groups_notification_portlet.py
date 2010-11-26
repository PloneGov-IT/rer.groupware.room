from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from zope.schema import vocabulary as schemavocab

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
        if request.form.has_key('addToGroup'):
            self.addUserToGroup(request.form.get('addToGroup'))
            
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
        user=self.pm.getAuthenticatedMember()
        user_groups=user.getGroups()
        if not user_groups:
            return []
        
        list_groups=[]
        for group in user_groups:
            group_obj=self.pg.getGroupById(group)
            if group_obj.getProperty('roomgroup'):
                group_title= group_obj.getProperty('title')
                group_id= group_obj.getId()
                if not group_title:
                    group_title= group_id
                group_dict={'title':group_title,
                            'id':group_id,
                            'notification_big':'%s.notifyBig'%group_id in user_groups,
                            'notification_small':'%s.notifySmall'%group_id in user_groups}
                list_groups.append(group_dict)
        return list_groups
    
    def addUserToGroup(self,group_id):
        group=self.pg.getGroupById(group_id)
        group_members=group.getMemberIds()
        userid=self.pm.getAuthenticatedMember().id
        if userid not in group_members:
            self.pg.addPrincipalToGroup(userid,group_id)
        else:
            self.pg.removePrincipalFromGroup(userid,group_id)
        return self.request.RESPONSE.redirect(self.context.absolute_url())
        
        
        
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
