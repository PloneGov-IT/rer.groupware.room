# -*- coding: utf-8 -*-
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.CMFCore.utils import getToolByName
from rer.groupware.room import logger
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.interfaces import IRoomArea
from zope.component._api import queryUtility
from zope.i18n import translate
from zope.interface import alsoProvides
from plone.portlets.interfaces import IPortletManager, IPortletAssignment, \
    IPortletAssignmentMapping
from zope.component import getMultiAdapter, getUtility, queryUtility
from redturtle.portlet.collection.rtcollectionportlet import \
    Assignment as CollectionAssignment


class CreateRoomStructure(object):

    def __init__(self, context, event):
        """
        @author: andrea cecchi
        This event creates some defined work areas
        """
        self.context = context
        self.request = self.context.REQUEST
        self.createAreas()

    def createAreas(self):
        """
        """
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
        polls_area_title = translate(_('area_polls_title',
                                        default="Polls"),
                                        context=self.request)

        self.createArea(id=self.generateId(news_area_title),
                        title=news_area_title,
                        portal_type="NewsArea",
                        types=['Folder', 'News Item'])
        self.createArea(id=self.generateId(blog_area_title),
                        title=blog_area_title,
                        portal_type="Blog")
        self.createArea(id=self.generateId(documents_area_title),
                        title=documents_area_title,
                        portal_type="DocumentsArea",
                        types=['Document', 'File', 'Image', 'Folder'])
        self.createArea(id=self.generateId(events_area_title),
                        title=events_area_title,
                        portal_type="EventsArea",
                        types=['Folder', 'Event'])
        self.createForum(forum_area_title)
        self.createArea(id=self.generateId(polls_area_title),
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
        if not area_id:
            logger.error("Problem creating Area: %s" % title)
            return ""
        logger.info("Created Area: %s" % title)
        area_obj = self.context.restrictedTraverse(area_id)

        #create topic before disallowing this type
        if portal_type not in ["PloneboardForum", "Blog"]:
            portal_types = []
            if portal_type == "NewsArea":
                portal_types = ['Folder', 'News Item']
            elif portal_type == "DocumentsArea":
                portal_types = ['Document', 'File', 'Image', 'Folder']
            elif portal_type == "EventsArea":
                portal_types = ['Event', 'Folder']
            elif portal_type == "PollsArea":
                portal_types = ['Folder', 'PlonePopoll']
            self.createCollection(folder=area_obj,
                                  id=id,
                                  title=title,
                                  set_as_default_view=True,
                                  portal_types=portal_types)

        #set allowed types
        if types:
            area_obj.setConstrainTypesMode(1)
            area_obj.setLocallyAllowedTypes(types)
            area_obj.setImmediatelyAddableTypes(types)

        alsoProvides(area_obj, IRoomArea)
        area_obj.reindexObject()
        return area_id

    def createForum(self, title):
        """
        Create a forum in the room
        """
        forum_id = self.context.invokeFactory(id=self.generateId(title),
                                              type_name='PloneboardForum',
                                              title=title,
                                              maxAttachmentSize=10000)
        if not forum_id:
            logger.error("Problem creating Area: %s" % title)
            return
        logger.info("Created Area: %s" % title)
        forum = self.context.restrictedTraverse(forum_id)

        alsoProvides(forum, IRoomArea)
        forum.reindexObject()

        wf_tool = getToolByName(self.context, 'portal_workflow')
        if self.context.getForumModerated():
            wf_tool.doActionFor(forum, 'make_moderated')
        return forum_id

    def createCollection(self, folder, id, title, **kwargs):
        """
        Create a collection in the area
        """
        #create topic query
        query = [{'i': 'path',
                  'o': 'plone.app.querystring.operation.string.path',
                  'v': "/".join(folder.getPhysicalPath())}]
        #optional settings
        portal_types = kwargs.get('portal_types', [])
        if portal_types:
            if "PlonePopoll" in portal_types:
                portal_types[portal_types.index('PlonePopoll')] = 'label_popoll'
            query.append(dict(i='portal_type',
                              o='plone.app.querystring.operation.selection.is',
                              v=portal_types))
        if kwargs.get('review_state', ''):
            query.append(dict(i='review_state',
                              o='plone.app.querystring.operation.selection.is',
                              v=kwargs.get('review_state', '')))
        #create the topic
        topic_id = folder.invokeFactory(id=id,
                                        type_name='Collection',
                                        title=title,
                                        query=query,
                                        sort_on='modified',
                                        sort_reversed=True)
        if not topic_id:
            logger.error("Problem creating collection for Area: %s" % folder.Title())
        logger.info("Collection created for Area: %s" % title)
        # topic = folder.restrictedTraverse(topic_id)
        # topic.selectViewTemplate(templateId='groupware_topic_view')
        if kwargs.get('set_as_default_view', False):
            #set topic as view of the folder
            folder.setDefaultPage(topic_id)

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = ' '.join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id


class CreateGroups(object):

    def __init__(self, context, event):
        """
        Create the groups for this room.
        These groups will be used to manage localroles
        """
        self.context = context
        groups_tool = getToolByName(self.context, 'portal_groups')
        room_id = self.context.getId()
        room_title = self.context.Title()
        sgm_groups = []
        #create members group
        groups_tool.addGroup(id='%s.members' % room_id,
                             title=translate(_(u"${room_title} members",
                                               mapping={u"room_title": room_title}),
                                             context=self.context.REQUEST))
        sgm_groups.append('%s.members' % room_id)
        #create members adv group
        groups_tool.addGroup(id='%s.membersAdv' % room_id,
                             title=translate(_(u"${room_title} membersAdv",
                                               mapping={u"room_title": room_title}),
                                             context=self.context.REQUEST))
        sgm_groups.append('%s.membersAdv' % room_id)
        #create coordinators group
        groups_tool.addGroup(id='%s.coordinators' % room_id,
                             title=translate(_(u"${room_title} coordinators",
                                               mapping={u"room_title": room_title}),
                                             context=self.context.REQUEST))
        #create hosts group
        groups_tool.addGroup(id='%s.hosts' % room_id,
                             title=translate(_(u"${room_title} hosts",
                                               mapping={u"room_title": room_title}),
                                             context=self.context.REQUEST))
        sgm_groups.append('%s.hosts' % room_id)

        #set SGM properties to allow coordinators to handle other groups
        self.addSGMEntries(sgm_groups, '%s.coordinators' % room_id)

    def addSGMEntries(self, managed_groups, coordinator):
        """
        Set SGM properties with new-created groups.
        """
        portal_properties = getToolByName(self.context, 'portal_properties', None)
        if not portal_properties:
            return
        sgm_properties = getattr(portal_properties, 'simple_groups_management_properties', None)
        if not sgm_properties:
            return
        sgm_groups = set(sgm_properties.getProperty('sgm_data', None))
        for group in managed_groups:
            sgm_groups.add('%s|%s' % (coordinator, group))

        sgm_properties._updateProperty('sgm_data', tuple(sgm_groups))
        logger.info('SGM properties set.')


class CreateSharing(object):

    def __init__(self, context, event):
        """
        Create the sharing localroles for already created groups.
        """
        self.context = context
        room_id = self.context.getId()
        pc = getToolByName(self.context, 'portal_catalog', None)
        #set local roles of the room
        self.setFolderLocalRoles(self.context,
                                 list_groups=[{'id':'%s.members' % room_id,
                                               'roles': ['Reader']},
                                              {'id':'%s.membersAdv' % room_id,
                                               'roles': ['Reader']},
                                              {'id':'%s.hosts' % room_id,
                                               'roles': ['Reader']},
                                              {'id':'%s.coordinators' % room_id,
                                               'roles': ['Reader']}])
        areas = pc(path="/".join(self.context.getPhysicalPath()),
                   object_provides=IRoomArea.__identifier__)
        for area in areas:
            groups = []
            if area.portal_type == "NewsArea":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Reader']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "DocumentsArea":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "EventsArea":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "PollsArea":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                         {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "PloneboardForum":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv', 'Reviewer']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "Blog":
                groups = [{'id': "%s.hosts" % room_id, 'roles': ['Reader']},
                          {'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            if groups:
                self.setFolderLocalRoles(area.getObject(), groups)
            logger.info("Sharing set")

    def setFolderLocalRoles(self, folder, list_groups):
        """
        Set the local roles for a given folder
        """
        #block the inherit
        folder.__ac_local_roles_block__ = True
        #set the local roles
        for group in list_groups:
            folder.manage_addLocalRoles(group.get('id'), group.get('roles'))
        #reindex the security
        folder.reindexObjectSecurity()


class CreateHomepage(object):

    def __init__(self, context, event):
        """
        Create the homepage view for this room.
        """
        self.context = context
        self.request = self.context.REQUEST
        self.createPortletPage()

    def createPortletPage(self):
        """
        """
        homepage_title = translate(_('room_homepage_title',
                                    default=u"Recent contents for this room"),
                                    context=self.request)
        portletpage_id = self.context.invokeFactory(id=self.generateId(homepage_title),
                                                    type_name='Portlet Page',
                                                    show_dates=True,
                                                    title=homepage_title)
        #set portletpage as default view for the room
        self.context.setDefaultPage(portletpage_id)
        portletpage = self.context.restrictedTraverse(portletpage_id)
        portletpage.manage_addLocalRoles('%s.membersAdv' % self.context.getId(), ['Editor', 'EditorAdv'])
        portletpage.manage_addLocalRoles('%s.coordinators' % self.context.getId(), ['Editor', 'EditorAdv', 'LocalManager'])
        logger.info("Created room homepage")

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = ' '.join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id
