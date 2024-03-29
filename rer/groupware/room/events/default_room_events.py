# -*- coding: utf-8 -*-
from plone import api
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlet.collection.collection import Assignment as CollectionAssignment
from plone.portlets.interfaces import IPortletAssignmentMapping, IPortletManager
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.SimpleGroupsManagement.interfaces import ISimpleGroupManagementSettings
from rer.groupware.room import logger
from rer.groupware.room import roomMessageFactory as _
from rer.groupware.room.interfaces import IRoomArea, IRoomGroupsSettingsSchema
from rer.groupware.room.utils import get_active_groups
from rer.groupware.room.utils import get_passive_groups
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.i18n import translate
from zope.interface import alsoProvides

try:
    from collective.portlet.discussion.discussionportlet import (
        Assignment as DiscussionAssignment,
    )
except:
    pass


class BaseEventClass(object):
    def __init__(self, context, event):
        """
        @author: andrea cecchi
        This event creates some defined work areas
        """
        self.context = context
        self.request = self.context.REQUEST

        language_tool = api.portal.get_tool("portal_languages")
        self.language = language_tool.getDefaultLanguage()

        try:
            if self.context.getRawLanguage():
                self.language = self.context.getRawLanguage()
        except:
            pass


class CreateRoomStructure(BaseEventClass):
    def __init__(self, context, event):
        """
        @author: andrea cecchi
        This event creates some defined work areas
        """
        super(CreateRoomStructure, self).__init__(context, event)
        self.createAreas()
        self.fixAreasOrder()

    def createAreas(self):
        """ """
        documents_area_title = translate(
            _("area_documents_title", default="Documents"),
            context=self.request,
            target_language=self.language,
        )
        events_area_title = translate(
            _("area_events_title", default="Agenda"),
            context=self.request,
            target_language=self.language,
        )
        # forum_area_title = translate(_('area_forum_title',
        #                                default="Forum"),
        #                              context=self.request,
        #                              target_language=self.language)
        # blog_area_title = translate(_('area_blog_title',
        #                               default="Blog"),
        #                             context=self.request,
        #                             target_language=self.language)
        news_area_title = translate(
            _("area_news_title", default="Bulletin board"),
            context=self.request,
            target_language=self.language,
        )
        polls_area_title = translate(
            _("area_polls_title", default="Polls"),
            context=self.request,
            target_language=self.language,
        )
        self.createArea(
            id=self.generateId(news_area_title),
            title=news_area_title,
            portal_type="NewsArea",
            types=["Folder", "News Item"],
        )
        # self.createArea(id=self.generateId(blog_area_title),
        #                 title=blog_area_title,
        #                 portal_type="Blog")
        self.createArea(
            id=self.generateId(documents_area_title),
            title=documents_area_title,
            portal_type="DocumentsArea",
            types=["Document", "File", "Image", "Folder"],
        )
        self.createArea(
            id=self.generateId(events_area_title),
            title=events_area_title,
            portal_type="EventsArea",
            types=["Folder", "Event"],
        )
        # RT self.createForum(forum_area_title)
        if "PlonePopoll" in getToolByName(self.context, "portal_types").objectIds():
            self.createArea(
                id=self.generateId(polls_area_title),
                title=polls_area_title,
                portal_type="PollsArea",
                types=["Folder", "PlonePopoll"],
            )
        else:
            logger.warn(
                f"{polls_area_title} not created because PlonePopoll is not installed"
            )

    def createArea(self, id, title, portal_type, types=[]):
        """
        Create an area with the given parameters
        """
        if id in self.context.objectIds():
            return id
        area_id = api.content.create(
            container=self.context,
            type=portal_type,
            id=id,
            title=title,
            language=self.language,
        )

        if not area_id:
            logger.error("Problem creating Area: %s" % title)
            return ""
        logger.info("Created Area: %s" % title)

        area_id_path = [x for x in area_id.getPhysicalPath()]

        area_obj = self.context.restrictedTraverse(area_id_path)

        # create topic before disallowing this type
        if portal_type not in ["PloneboardForum", "Blog", "DocumentsArea"]:
            portal_types = []
            if portal_type == "NewsArea":
                portal_types = ["Folder", "News Item"]
            elif portal_type == "EventsArea":
                portal_types = ["Event", "Folder"]
            elif portal_type == "PollsArea":
                portal_types = ["Folder", "PlonePopoll"]
            self.createCollection(
                folder=area_obj,
                id=id,
                title=title,
                set_as_default_view=True,
                portal_types=portal_types,
            )

        if portal_type == "DocumentsArea":
            self.createCollection(
                folder=area_obj,
                id=id,
                title=title,
                set_recurse="True",
                set_as_default_view=False,
                portal_types=["Document", "File", "Image"],
            )

            self.createCollection(
                folder=area_obj,
                id=translate(
                    _("documents-and-folders"),
                    context=self.context.REQUEST,
                    target_language=self.language,
                ),
                title=translate(
                    _("Documents and folders"),
                    context=self.context.REQUEST,
                    target_language=self.language,
                ),
                set_as_default_view=True,
                portal_types=["Document", "File", "Image", "Folder"],
            )
        # set allowed types
        if types:
            behavior = ISelectableConstrainTypes(area_obj)
            behavior.setConstrainTypesMode(1)
            behavior.setLocallyAllowedTypes(types)
            behavior.setImmediatelyAddableTypes(types)

        alsoProvides(area_obj, IRoomArea)
        area_obj.reindexObject()
        return area_id

    def createForum(self, title):
        """
        Create a forum in the room
        """
        forum_id = self.context.invokeFactory(
            id=self.generateId(title),
            type_name="PloneboardForum",
            title=title,
            maxAttachmentSize=10000,
            language=self.language,
        )
        if not forum_id:
            logger.error("Problem creating Area: %s" % title)
            return
        logger.info("Created Area: %s" % title)
        forum = self.context.restrictedTraverse(forum_id)

        alsoProvides(forum, IRoomArea)
        forum.reindexObject()

        wf_tool = getToolByName(self.context, "portal_workflow")
        if self.context.getForumModerated():
            wf_tool.doActionFor(forum, "make_moderated")
        return forum_id

    def createCollection(self, folder, id, title, **kwargs):
        """
        Create a collection in the area
        """
        # create topic query
        query = [
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/".join(folder.getPhysicalPath()),
            }
        ]
        # optional settings
        portal_types = kwargs.get("portal_types", [])
        if portal_types:
            query.append(
                dict(
                    i="portal_type",
                    o="plone.app.querystring.operation.selection.any",
                    v=portal_types,
                )
            )
        if kwargs.get("review_state", ""):
            query.append(
                dict(
                    i="review_state",
                    o="plone.app.querystring.operation.selection.is",
                    v=kwargs.get("review_state", ""),
                )
            )
        # create the topic
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        collection_type = getattr(groups_settings, "collection_type", "Collection")
        topic_id = api.content.create(
            container=folder,
            type=collection_type,
            id=id,
            title=title,
            language=self.language,
            query=query,
            sort_on="modified",
            sort_reversed=True,
        )

        if not topic_id:
            logger.error("Problem creating collection for Area: %s" % folder.Title())
        logger.info("Collection created for Area: %s" % title)
        # topic = folder.restrictedTraverse(topic_id)
        # topic.selectViewTemplate(templateId='groupware_topic_view')
        if kwargs.get("set_as_default_view", False):
            # set topic as view of the folder
            folder.setDefaultPage(topic_id.id)

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = " ".join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id

    def fixAreasOrder(self):
        """
        Reorder areas alphabetically in the folder
        """
        room = self.context
        pc = getToolByName(room, "portal_catalog", None)
        plone_utils = getToolByName(room, "plone_utils")
        areas = pc(
            path={"query": "/".join(room.getPhysicalPath()), "depth": 1},
            object_provides=IRoomArea.__identifier__,
            sort_on="sortable_title",
        )
        for index, area in enumerate(areas):
            room.moveObjectToPosition(area.getId, index)
            plone_utils.reindexOnReorder(room)
        logger.info("Ordered Areas")


class CreateGroups(BaseEventClass):
    def __init__(self, context, event):
        """
        Create the groups for this room.
        These groups will be used to manage localroles
        """
        super(CreateGroups, self).__init__(context, event)
        groups_tool = getToolByName(self.context, "portal_groups")
        room_id = self.context.getId()
        room_title = self.context.Title()
        active_groups = get_active_groups()
        passive_groups = get_passive_groups()
        # create a default group that contains all active groups
        uber_group_id = "%s.users" % room_id
        groups_tool.addGroup(
            id=uber_group_id,
            title=translate(
                _("${room_title} Users", mapping={"room_title": room_title}),
                context=self.context.REQUEST,
                target_language=self.language,
            ),
        )
        if not active_groups:
            logger.warning(
                "No default groups set in the portal. We don't create any specific group for this room."
            )
            return
        sgm_groups = []
        # now create active groups and add them to uber_group
        for group in active_groups:
            group_id = "%s.%s" % (room_id, group["group_id"])
            group_title = "%s %s" % (room_title, group["group_title"])
            res = groups_tool.addGroup(id=group_id, title=group_title)
            if res:
                groups_tool.addPrincipalToGroup(group_id, uber_group_id)
                logger.info("Created active group %s" % group_id)
                if group["group_id"] != "coordinators":
                    sgm_groups.append(group_id)

        for group in passive_groups:
            group_id = "%s.%s" % (room_id, group["group_id"])
            group_title = "%s %s" % (room_title, group["group_title"])
            res = groups_tool.addGroup(id=group_id, title=group_title)
            if res:
                logger.info("Created passive group %s" % group_id)
                sgm_groups.append(group_id)

        self.addSGMEntries(sgm_groups, "%s.coordinators" % room_id)

    def addSGMEntries(self, managed_groups, coordinator):
        """
        Set SGM properties with new-created groups.
        """
        old_sgm_data = api.portal.get_registry_record(
            "sgm_data", interface=ISimpleGroupManagementSettings
        )
        sgm_data = list(old_sgm_data)
        for group in managed_groups:
            sgm_data.append("%s|%s" % (coordinator, group))

        api.portal.set_registry_record(
            "sgm_data", tuple(sgm_data), interface=ISimpleGroupManagementSettings
        )
        logger.info("SGM properties set.")


class CreateSharing(BaseEventClass):
    def __init__(self, context, event):
        """
        Create the sharing localroles for already created groups.
        """
        super(CreateSharing, self).__init__(context, event)
        room_id = self.context.getId()
        pc = getToolByName(self.context, "portal_catalog", None)
        # set local roles of the room
        self.setFolderLocalRoles(
            self.context,
            list_groups=[
                {"id": "%s.users" % room_id, "roles": ["Active User"]},
                {"id": "%s.hosts" % room_id, "roles": ["Reader"]},
            ],
            roles_block=True,
        )
        areas = pc(
            path="/".join(self.context.getPhysicalPath()),
            object_provides=IRoomArea.__identifier__,
        )
        for area in areas:
            groups = []
            if area.portal_type == "NewsArea":
                groups = [
                    {
                        "id": "%s.membersAdv" % room_id,
                        "roles": ["Contributor", "Editor", "EditorAdv"],
                    },
                    {
                        "id": "%s.coordinators" % room_id,
                        "roles": [
                            "LocalManager",
                            "Contributor",
                            "Editor",
                            "EditorAdv",
                            "Reviewer",
                        ],
                    },
                ]
            elif area.portal_type == "DocumentsArea":
                groups = [
                    {"id": "%s.members" % room_id, "roles": ["Contributor", "Editor"]},
                    {
                        "id": "%s.membersAdv" % room_id,
                        "roles": ["Contributor", "Editor", "EditorAdv"],
                    },
                    {
                        "id": "%s.coordinators" % room_id,
                        "roles": [
                            "LocalManager",
                            "Contributor",
                            "Editor",
                            "EditorAdv",
                            "Reviewer",
                        ],
                    },
                ]
            elif area.portal_type == "EventsArea":
                groups = [
                    {"id": "%s.members" % room_id, "roles": ["Contributor", "Editor"]},
                    {
                        "id": "%s.membersAdv" % room_id,
                        "roles": ["Contributor", "Editor", "EditorAdv"],
                    },
                    {
                        "id": "%s.coordinators" % room_id,
                        "roles": [
                            "LocalManager",
                            "Contributor",
                            "Editor",
                            "EditorAdv",
                            "Reviewer",
                        ],
                    },
                ]
            elif area.portal_type == "PollsArea":
                groups = [
                    {"id": "%s.members" % room_id, "roles": ["Contributor", "Editor"]},
                    {
                        "id": "%s.membersAdv" % room_id,
                        "roles": ["Contributor", "Editor", "EditorAdv"],
                    },
                    {
                        "id": "%s.coordinators" % room_id,
                        "roles": [
                            "LocalManager",
                            "Contributor",
                            "Editor",
                            "EditorAdv",
                            "Reviewer",
                        ],
                    },
                ]
            elif area.portal_type == "PloneboardForum":
                groups = [
                    {"id": "%s.members" % room_id, "roles": ["Contributor", "Editor"]},
                    {
                        "id": "%s.membersAdv" % room_id,
                        "roles": ["Contributor", "Editor", "EditorAdv", "Reviewer"],
                    },
                    {
                        "id": "%s.coordinators" % room_id,
                        "roles": [
                            "LocalManager",
                            "Contributor",
                            "Editor",
                            "EditorAdv",
                            "Reviewer",
                        ],
                    },
                ]
            # elif area.portal_type == "Blog":
            #     groups = [{'id': '%s.members' % room_id, 'roles': ['Contributor', 'Editor']},
            #               {'id': '%s.membersAdv' % room_id, 'roles': [
            #                   'Contributor', 'Editor', 'EditorAdv']},
            #               {'id': '%s.coordinators' % room_id, 'roles': ['LocalManager', 'Contributor', 'Editor', 'EditorAdv', 'Reviewer']}]
            if groups:
                self.setFolderLocalRoles(area.getObject(), groups)
            logger.info("Sharing set")

    def setFolderLocalRoles(self, folder, list_groups, roles_block=False):
        """
        Set the local roles for a given folder
        """
        if roles_block:
            # block the inherit
            folder.__ac_local_roles_block__ = True
        # set the local roles
        for group in list_groups:
            folder.manage_addLocalRoles(group.get("id"), group.get("roles"))
        # reindex the security
        folder.reindexObjectSecurity()


class CreateHomepage(BaseEventClass):

    left_manager_id = "collective.portletpage.firstcolumn"
    right_manager_id = "collective.portletpage.secondcolumn"
    portletpage_type = "Portlet Page"

    def __init__(self, context, event):
        """
        Create the homepage view for this room.
        """
        super(CreateHomepage, self).__init__(context, event)
        self.createPortletPage()

    def createPortletPage(self):
        """ """
        homepage_title = translate(
            _("room_homepage_title", default="Recent contents for this room"),
            context=self.request,
            target_language=self.language,
        )
        portletpage_id = self.context.invokeFactory(
            id=self.generateId(homepage_title),
            type_name=self.portletpage_type,
            show_dates=True,
            title=homepage_title,
            language=self.language,
        )
        # set portletpage as default view for the room
        self.context.setDefaultPage(portletpage_id)
        portletpage = self.context.restrictedTraverse(portletpage_id)
        portletpage.manage_addLocalRoles(
            "%s.membersAdv" % self.context.getId(), ["Editor", "EditorAdv"]
        )
        portletpage.manage_addLocalRoles(
            "%s.coordinators" % self.context.getId(),
            ["Editor", "EditorAdv", "LocalManager"],
        )
        logger.info("Created room homepage")
        # RT self.createHomepagePortlets(portletpage)

    def createHomepagePortlets(self, portletpage):
        """ """
        # setup portlet managers

        left_manager = getUtility(
            IPortletManager, name=self.left_manager_id, context=portletpage
        )
        right_manager = getUtility(
            IPortletManager, name=self.right_manager_id, context=portletpage
        )
        left_mapping = getMultiAdapter(
            (portletpage, left_manager), IPortletAssignmentMapping
        )
        right_mapping = getMultiAdapter(
            (portletpage, right_manager), IPortletAssignmentMapping
        )
        # left column portlets
        # documents
        assignment, portlet_id = self.createCollectionPortlet(
            area_type="DocumentsArea", limit=5, use_default_collection=False
        )
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment
        # news
        assignment, portlet_id = self.createCollectionPortlet(
            area_type="NewsArea", limit=3, use_default_collection=True
        )
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment
        # events
        assignment, portlet_id = self.createCollectionPortlet(
            area_type="EventsArea", limit=3, use_default_collection=True
        )
        if assignment and portlet_id:
            left_mapping[portlet_id] = assignment

        # right column portlets
        # discussion
        try:
            assignment, portlet_id = self.createDiscussionPortlet()
            if assignment and portlet_id:
                right_mapping[portlet_id] = assignment
        except:
            pass

        # forum
        # assignment, portlet_id = self.createForumPortlet()
        # if assignment and portlet_id:
        #    right_mapping[portlet_id] = assignment

        # blog disabled
        # assignment, portlet_id = self.createBlogPortlet()
        # if assignment and portlet_id:
        #     right_mapping[portlet_id] = assignment
        # polls
        assignment, portlet_id = self.createCollectionPortlet(
            area_type="PollsArea", limit=3, use_default_collection=True
        )
        if assignment and portlet_id:
            right_mapping[portlet_id] = assignment

        logger.info("Created homepage portlets")

    def createCollectionPortlet(self, area_type, limit, use_default_collection=True):
        """
        imposta l'assignment per la collection portlet
        """
        pc = getToolByName(self.context, "portal_catalog", None)
        areas = pc(path="/".join(self.context.getPhysicalPath()), portal_type=area_type)
        if len(areas) != 1:
            return None, ""
        area = areas[0]
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        collection_type = getattr(groups_settings, "collection_type", "Collection")
        query = {
            "path": {"query": area.getPath(), "depth": 1},
            "portal_type": collection_type,
        }
        if not use_default_collection:
            query["id"] = area.getId
        collections = pc(**query)
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        collection_path = ""
        if not collections:
            return None, ""
        elif collections.actual_result_count == 1:
            collection_path = (
                collections[0]
                .getPath()
                .replace(portal_state.navigation_root_path(), "")
            )
        else:
            for collection in collections:
                collection_obj = collection.getObject()
                context_state = getMultiAdapter(
                    (collection_obj, self.request), name="plone_context_state"
                )
                if context_state.is_default_page():
                    collection_path = collection.getPath().replace(
                        portal_state.navigation_root_path(), ""
                    )
        if not collection_path:
            return None, ""
        assignment = CollectionAssignment(
            header=area.Title,
            target_collection=collection_path,
            show_dates=True,
            limit=limit,
            template_id="groupware_collection_portlet_view",
            css_class="portlet%s" % area.Title,
            show_more=True,
        )

        return assignment, area.getId

    # def createBlogPortlet(self):
    #     pc = getToolByName(self.context, 'portal_catalog', None)
    #     areas = pc(
    #         path="/".join(self.context.getPhysicalPath()), portal_type="Blog")
    #     if len(areas) != 1:
    #         return None, ''
    #     area = areas[0]
    #     portal_state = getMultiAdapter(
    #         (self.context, self.request), name='plone_portal_state')
    #     assignment = BlogAssignment(portletTitle=translate(_("Last blog posts"),
    #                                                        context=self.request,
    #                                                        target_language=self.language),
    #                                 blogFolder=area.getPath().replace(
    #                                     portal_state.navigation_root_path(), ''),
    #                                 entries=3)
    #     return assignment, "blog"

    def createDiscussionPortlet(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        area_path = "/".join(self.context.getPhysicalPath())
        assignment = DiscussionAssignment(
            portletTitle=translate(
                _("Discussions"), context=self.request, target_language=self.language
            ),
            discussionFolder=area_path.replace(portal_state.navigation_root_path(), ""),
            nDiscussions=3,
        )
        return assignment, "discussions"

    # RT#
    # def createForumPortlet(self):
    #     pc = getToolByName(self.context, 'portal_catalog', None)
    #     areas = pc(path="/".join(self.context.getPhysicalPath()), portal_type="PloneboardForum")
    #     if len(areas) != 1:
    #         return None, ''
    #     area = areas[0]
    #     assignment = PloneboardAssignment(title=translate(_("Last forum discussions"),
    #                                                         context=self.request,
    #                                                         target_language=self.language),
    #                                     forum=area.UID,
    #                                     count=3)
    #     return assignment, 'forum'

    def generateId(self, title):
        """
        Obtain a nice id from the title in two steps:
        first we remove forbidden
        chars and the we ensure ourselves it is unique
        """
        title = " ".join(title.split())
        id = queryUtility(IURLNormalizer).normalize(title)
        return id
