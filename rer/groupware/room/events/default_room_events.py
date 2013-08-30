# -*- coding: utf-8 -*-
from collective.portlet.blogstarentries.blogstarlastentries import Assignment as BlogAssignment
from collective.portlet.discussion.discussionportlet import Assignment as DiscussionAssignment
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Ploneboard.portlet.recent import Assignment as PloneboardAssignment
from redturtle.portlet.collection.rtcollectionportlet import Assignment as CollectionAssignment
from rer.groupware.room import logger
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.interfaces import IRoomArea
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.i18n import translate
from zope.interface import alsoProvides
from Acquisition import aq_inner
from zope.component import getMultiAdapter


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
        if portal_type not in ["PloneboardForum", "Blog", "DocumentsArea"]:
            portal_types = []
            if portal_type == "NewsArea":
                portal_types = ['Folder', 'News Item']
            elif portal_type == "EventsArea":
                portal_types = ['Event', 'Folder']
            elif portal_type == "PollsArea":
                portal_types = ['Folder', 'PlonePopoll']
            self.createCollection(folder=area_obj,
                                  id=id,
                                  title=title,
                                  set_as_default_view=True,
                                  portal_types=portal_types)

        if portal_type == "DocumentsArea":
            self.createCollection(folder=area_obj,
                                  id=id,
                                  title=title,
                                  set_recurse="True",
                                  set_as_default_view=False,
                                  portal_types=['Document', 'File', 'Image'])

            self.createCollection(folder=area_obj,
                                  id=translate(_("documents-and-folders"), context=self.context.REQUEST),
                                  title=translate(_("Documents and folders"), context=self.context.REQUEST),
                                  set_as_default_view=True,
                                  portal_types=['Document', 'File', 'Image', 'Folder'])
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
            query.append(dict(i='portal_type',
                              o='plone.app.querystring.operation.selection.is',
                              v=portal_types))
        if kwargs.get('review_state', ''):
            query.append(dict(i='review_state',
                              o='plone.app.querystring.operation.selection.is',
                              v=kwargs.get('review_state', '')))
        #create the topic
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        collection_type = getattr(groups_settings, 'collection_type', "Collection")
        topic_id = folder.invokeFactory(id=id,
                                        type_name=collection_type,
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
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        active_groups = getattr(groups_settings, 'active_groups', None)
        passive_groups = getattr(groups_settings, 'passive_groups', None)
        #create a default group that contains all active groups
        uber_group_id = "%s.users" % room_id
        groups_tool.addGroup(id=uber_group_id,
                             title=translate(_(u"${room_title} Users",
                                               mapping={u"room_title": room_title}),
                                               context=self.context.REQUEST))
        if not active_groups:
            logger.warning("No default groups set in the portal. We don't create any specific group for this room.")
            return
        sgm_groups = []
        #now create active groups and add them to uber_group
        for group in active_groups:
            group_id = '%s.%s' % (room_id, group.group_id)
            group_title = '%s %s' % (room_title, group.group_title)
            res = groups_tool.addGroup(id=group_id,
                                       title=group_title)
            if res:
                groups_tool.addPrincipalToGroup(group_id, uber_group_id)
                logger.info("Created active group %s" % group_id)
                sgm_groups.append(group_id)

        for group in passive_groups:
            group_id = '%s.%s' % (room_id, group.group_id)
            group_title = '%s %s' % (room_title, group.group_title)
            res = groups_tool.addGroup(id=group_id,
                                       title=group_title)
            if res:
                logger.info("Created passive group %s" % group_id)
                sgm_groups.append(group_id)

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
                                 list_groups=[{'id':'%s.users' % room_id,
                                               'roles': ['Active User']},
                                              {'id': '%s.hosts' % room_id,
                                                'roles': ['Reader']}],
                                 roles_block=True)
        areas = pc(path="/".join(self.context.getPhysicalPath()),
                   object_provides=IRoomArea.__identifier__)
        for area in areas:
            groups = []
            if area.portal_type == "NewsArea":
                groups = [{'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "DocumentsArea":
                groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "EventsArea":
                groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "PollsArea":
                groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                         {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "PloneboardForum":
                groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv', 'Reviewer']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            elif area.portal_type == "Blog":
                groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
                          {'id': '%s.membersAdv' % room_id, 'roles': ['Contributor', 'Editor', 'EditorAdv']},
                          {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            if groups:
                self.setFolderLocalRoles(area.getObject(), groups)
            logger.info("Sharing set")

    def setFolderLocalRoles(self, folder, list_groups, roles_block=False):
        """
        Set the local roles for a given folder
        """
        if roles_block:
            #block the inherit
            folder.__ac_local_roles_block__ = True
        #set the local roles
        for group in list_groups:
            folder.manage_addLocalRoles(group.get('id'), group.get('roles'))
        #reindex the security
        folder.reindexObjectSecurity()


class CreateHomepage(object):

    left_manager_id = 'collective.portletpage.firstcolumn'
    right_manager_id = 'collective.portletpage.secondcolumn'
    portletpage_type = 'Portlet Page'

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
                                                    type_name=self.portletpage_type,
                                                    show_dates=True,
                                                    title=homepage_title)
        #set portletpage as default view for the room
        self.context.setDefaultPage(portletpage_id)
        portletpage = self.context.restrictedTraverse(portletpage_id)
        portletpage.manage_addLocalRoles('%s.membersAdv' % self.context.getId(), ['Editor', 'EditorAdv'])
        portletpage.manage_addLocalRoles('%s.coordinators' % self.context.getId(), ['Editor', 'EditorAdv', 'LocalManager'])
        logger.info("Created room homepage")
        self.createHomepagePortlets(portletpage)

    def createHomepagePortlets(self, portletpage):
        """
        """
        #setup portlet managers
        left_manager = getUtility(IPortletManager,
                                  name=self.left_manager_id,
                                  context=portletpage)
        right_manager = getUtility(IPortletManager,
                                  name=self.right_manager_id,
                                  context=portletpage)
        left_mapping = getMultiAdapter((portletpage, left_manager), IPortletAssignmentMapping)
        right_mapping = getMultiAdapter((portletpage, right_manager), IPortletAssignmentMapping)
        #left column portlets
        #documents
        assignment, portlet_id = self.createCollectionPortlet(area_type="DocumentsArea",
                                                              limit=5,
                                                              use_default_collection=False)
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment
        #news
        assignment, portlet_id = self.createCollectionPortlet(area_type="NewsArea",
                                                              limit=3,
                                                              use_default_collection=True)
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment
        #events
        assignment, portlet_id = self.createCollectionPortlet(area_type="EventsArea",
                                                              limit=3,
                                                              use_default_collection=True)
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment

        #right column portlets
        #discussion
        assignment, portlet_id = self.createDiscussionPortlet()
        if assignment and portlet_id:
            right_mapping[portlet_id] = assignment
        #forum
        assignment, portlet_id = self.createForumPortlet()
        if assignment and portlet_id:
            right_mapping[portlet_id] = assignment

        #blog
        assignment, portlet_id = self.createBlogPortlet()
        if assignment and portlet_id:
            right_mapping[portlet_id] = assignment
        #polls
        assignment, portlet_id = self.createCollectionPortlet(area_type="PollsArea",
                                                              limit=3,
                                                              use_default_collection=True)
        if assignment and portlet_id:
            right_mapping[portlet_id] = assignment

        logger.info("Created homepage portlets")

    def createCollectionPortlet(self, area_type, limit, use_default_collection=True):
        """
        imposta l'assignment per la collection portlet
        """
        pc = getToolByName(self.context, 'portal_catalog', None)
        areas = pc(path="/".join(self.context.getPhysicalPath()), portal_type=area_type)
        if len(areas) != 1:
            return None, ''
        area = areas[0]
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        collection_type = getattr(groups_settings, 'collection_type', "Collection")
        query = {'path': {"query": area.getPath(), "depth": 1},
                 'portal_type': collection_type}
        if not use_default_collection:
            query['id'] = area.getId
        collections = pc(**query)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        collection_path = ""
        if not collections:
            return None, ''
        elif collections.actual_result_count == 1:
            collection_path = collections[0].getPath().replace(portal_state.navigation_root_path(), '')
        else:
            for collection in collections:
                collection_obj = collection.getObject()
                context_state = getMultiAdapter((collection_obj, self.request), name=u'plone_context_state')
                if context_state.is_default_page():
                    collection_path = collection.getPath().replace(portal_state.navigation_root_path(), '')
        if not collection_path:
            return None, ''
        assignment = CollectionAssignment(header=area.Title,
                                        target_collection=collection_path,
                                        show_dates=True,
                                        limit=limit,
                                        template_id="groupware_collection_portlet_view",
                                        css_class="portlet%s" % area.Title,
                                        show_more=True)

        return assignment, area.getId

    def createBlogPortlet(self):
        pc = getToolByName(self.context, 'portal_catalog', None)
        areas = pc(path="/".join(self.context.getPhysicalPath()), portal_type="Blog")
        if len(areas) != 1:
            return None, ''
        area = areas[0]
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        assignment = BlogAssignment(portletTitle=translate(_(u"Last blog posts"),
                                                            context=self.request),
                                    blogFolder=area.getPath().replace(portal_state.navigation_root_path(), ''),
                                    entries=3)
        return assignment, "blog"

    def createDiscussionPortlet(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        area_path = "/".join(self.context.getPhysicalPath())
        assignment = DiscussionAssignment(portletTitle=translate(_(u"Discussions"),
                                                                 context=self.request),
                                          discussionFolder=area_path.replace(portal_state.navigation_root_path(), ''),
                                          nDiscussions=3)
        return assignment, "discussions"

    def createForumPortlet(self):
        pc = getToolByName(self.context, 'portal_catalog', None)
        areas = pc(path="/".join(self.context.getPhysicalPath()), portal_type="PloneboardForum")
        if len(areas) != 1:
            return None, ''
        area = areas[0]
        assignment = PloneboardAssignment(title=translate(_(u"Last forum discussions"),
                                                            context=self.request),
                                        forum=area.UID,
                                        count=3)
        return assignment, 'forum'

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = ' '.join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id
