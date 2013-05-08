# -*- coding: utf-8 -*-
from zope.i18n import translate
from rer.groupware.room import roomMessageFactory as _
from plone.i18n.normalizer.interfaces import IURLNormalizer
from zope.component._api import queryUtility
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides
from rer.groupware.room.interfaces import IRoomArea


class CreateRoomStructure(object):

    def __init__(self, context, event):
        """
        @author: andrea cecchi
        This event creates some defined work areas
        """
        self.context = context
        self.request = self.context.REQUEST
        documents_area_title = translate(_('area_documents_title',
                                    default="Documents"),
                                    context=self.request)
        events_area_title = translate(_('area_events_title',
                                        default="Events"),
                                        context=self.request)
        forum_area_title = translate(_('area_forum_title',
                                        default="Forum"),
                                        context=self.request)
        blog_area_title = translate(_('area_blog_title',
                                        default="Blog"),
                                        context=self.request)
        news_area_title = translate(_('area_news_title',
                                        default="News"),
                                        context=self.request)
        # projects_area_title = translate(_('area_projects_title',
        #                                 default="Projects"),
        #                                 context=self.request)
        polls_area_title = translate(_('area_polls_title',
                                        default="Polls"),
                                        context=self.request)

        news_area = self.createArea(id=self.generateId(news_area_title),
                             title=news_area_title,
                             portal_type="NewsArea",
                             types=['Folder', 'News Item'])
        blog_area = self.createArea(id=self.generateId(blog_area_title),
                             title=blog_area_title,
                             portal_type="Blog")
        documents_area = self.createArea(id=self.generateId(documents_area_title),
                                  title=documents_area_title,
                                  portal_type="DocumentsArea",
                                  types=['Document', 'File', 'Image', 'Folder'])
        events_area = self.createArea(id=self.generateId(events_area_title),
                               title=events_area_title,
                               portal_type="EventsArea",
                               types=['Folder', 'Event'])
        forum_area = self.createForum(forum_area_title)
        
        # projects=self.createArea(id=self.generateId(projects_title),
        #                          title=projects_title,
        #                          portal_type="ProjectsArea",
        #                          types=['Folder','Project'],
        #                          collection_types=['Project', 'Folder'],
        #                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
        #                                  {'id':'%s.members'%base_id,'roles':['Contributor','Editor','Employee']},
        #                                  {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Employee']},
        #                                  {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Projectmanager','Contributor','Editor','EditorAdv','Reviewer']},]
        #                          )

        polls_area = self.createArea(id=self.generateId(polls_area_title),
                              title=polls_area_title,
                              portal_type="PollsArea",
                              types=['Folder', 'PlonePopoll'])

    def createArea(self, id, title, portal_type, types=[]):
        """
        Create an area with the given parameters
        """
        area_id = self.context.invokeFactory(id=id,
                                             type_name=portal_type,
                                             title=title)
        area_obj = self.context.restrictedTraverse(area_id)
        #set allowed types
        if types:
            area_obj.setConstrainTypesMode(1)
            area_obj.setLocallyAllowedTypes(types)
            area_obj.setImmediatelyAddableTypes(types)

        alsoProvides(area_obj, IRoomArea)
        area_obj.reindexObject()
        return area_obj

    def createForum(self, title):
        """
        Create a forum in the room
        """
        room_id = self.context.getId()
        forum_id = self.context.invokeFactory(id=self.generateId(title),
                                              type_name='PloneboardForum',
                                              title=title,
                                              maxAttachmentSize=10000)
        if not forum_id:
            return
        forum = self.context.restrictedTraverse(forum_id)

        alsoProvides(forum, IRoomArea)
        forum.reindexObject()

        wf_tool = getToolByName(self.context, 'portal_workflow')
        if self.context.getForumModerated():
            wf_tool.doActionFor(forum, 'make_moderated')
        return forum

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = ' '.join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id


def createGroups(room, event):
    """
    This event throw some specified events for room initial setup
    """


def createRules(room, event):
    """
    This event throw some specified events for room initial setup
    """


def createHomePage(room, event):
    """
    This event throw some specified events for room initial setup
    """


def createSharing(room, event):
    """
    This event throw some specified events for room initial setup
    """