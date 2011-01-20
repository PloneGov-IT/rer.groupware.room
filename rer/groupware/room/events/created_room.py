# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.PlonePopoll.browser.popoll import Assignment as PopollAssignment
from Products.Ploneboard.portlet.recent_contextual import \
    Assignment as PloneboardAssignment
from collective.contentrules.mailtogroup.actions.mail import MailGroupAction
from collective.portlet.blogstarentries.blogstarlastentries import \
    Assignment as BlogAssignment
from collective.portlet.discussion.discussionportlet import \
    Assignment as DiscussionAssignment
from plone.app.contentrules.conditions.portaltype import PortalTypeCondition
from plone.app.contentrules.rule import Rule, get_assignments
from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager, \
    IRuleStorage
from plone.portlets.interfaces import IPortletManager, IPortletAssignment, \
    IPortletAssignmentMapping
from redturtle.portlet.collection.rtcollectionportlet import \
    Assignment as CollectionAssignment
from rer.groupware.custom.portlets.managers import \
    Assignment as ProjectsAssignment
from zope.app.container.interfaces import IObjectRemovedEvent, INameChooser
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import logging
logger = logging.getLogger('rer.groupware.room')

class CreateRoomStructure(object):

    def __init__(self, context, event):
        """
        @author: andrea cecchi
        
        """
        self.context = context
        self.translation_service=getToolByName(self.context,'translation_service')
        self.root_path='/'.join(self.context.portal_url.getPortalObject().getPhysicalPath())
        self.portlet_page_order={'collective.portletpage.firstcolumn':{},
                                 'collective.portletpage.secondcolumn':{}}
        #create room's areas
        self.portlet_page = self.createPortletPage()
        self.createGroups()
        self.areas=self.createAreas()
        #create the rules
        self.createRules(rule_type='ruleNewsEvents',
                        group_type='notifyNewsEvents',
                        types_list=set(['News Item','Event']))
        self.createRules(rule_type='ruleDocs',
                        group_type='notifyDocs',
                        types_list=set(['Document','File','Image','Collection']))
        
        #set local roles of the room
        self.setFolderLocalRoles(self.context,
                                 list_groups=[{'id':'%s.members'%self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.membersAdv'%self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.hosts'%self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.coordinators'%self.context.getId(),'roles':['Reader']},])
        
        self.adjustPortletPage()
        logger.info('Stanza creata')
        
    #WE CREATE THE PORTLETPAGE
    def createPortletPage(self):
        """
        @author: andrea cecchi
        Crea una portletpage di partenza, da assegnare come vista predefinita per la stanza
        """
        portletpage_id=self.context.invokeFactory(id="i-contenuti-piu-recenti",
                                                  type_name='Portlet Page',
                                                  show_dates=True,
                                                  title=u"I contenuti più recenti")
        
        #imposta la portletpage come vista pedefinita della stanza
        self.context.setDefaultPage(portletpage_id)
        
        portletpage=self.context.restrictedTraverse(portletpage_id)
        portletpage.manage_addLocalRoles('%s.membersAdv'%self.context.getId(),['Editor','EditorAdv'])
        portletpage.manage_addLocalRoles('%s.coordinators'%self.context.getId(),['Editor','EditorAdv','LocalManager'])
        return portletpage
    
    #FIRST WE CREATE THE GROUPS
    def createGroups(self):
        groups_tool=getToolByName(self.context,'portal_groups')
        room_id=self.context.getId()
        room_title=self.context.Title()
#        room_group=groups_tool.addGroup(id=room_id,title=room_title)
#        if not room_group:
#            return
#        groups_tool.getGroupById(room_id).setProperties(roomgroup=True)
        sgm_groups=[]
        groups_tool.addGroup(id='%s.members' %room_id,title='%s members' %room_title)
        sgm_groups.append('%s.members' %room_id)
        groups_tool.addGroup(id='%s.membersAdv' %room_id,title='%s membersAdv' %room_title)
        sgm_groups.append('%s.membersAdv' %room_id)
        groups_tool.addGroup(id='%s.notifyDocs' %room_id,title='%s notifyDocs' %room_title)
        groups_tool.addGroup(id='%s.notifyNewsEvents' %room_id,title='%s notifyNewsEvents' %room_title)
        groups_tool.addGroup(id='%s.coordinators' %room_id,title='%s coordinators' %room_title)
        groups_tool.addGroup(id='%s.hosts'%room_id,title='%s hosts' %room_title)
        sgm_groups.append('%s.hosts' %room_id)
        
        self.addSGMEntries(sgm_groups,'%s.coordinators' %room_id)
        
    def addSGMEntries(self,managed_groups,coordinator):
        portal_properties = getToolByName(self.context, 'portal_properties', None)
        if not portal_properties:
            return
        sgm_properties = getattr(portal_properties, 'simple_groups_management_properties', None)
        if not sgm_properties:
            return
        sgm_groups = set(sgm_properties.getProperty('sgm_data', None))
        for group in managed_groups:
            sgm_groups.add('%s|%s' %(coordinator,group))
        
        sgm_properties._updateProperty('sgm_data',tuple(sgm_groups))
        logger.info('SGM properties set.')
        
        
    #THEN WE CREATE THE AREAS
    def createForum(self):
        room_id=self.context.getId()
        forum_id=self.context.invokeFactory(id="forum",
                                            type_name='PloneboardForum',
                                            title="Forum")
        if not forum_id:
            return
        forum=self.context.restrictedTraverse(forum_id)
        wf_tool=getToolByName(self.context,'portal_workflow')
        wf_tool.doActionFor(forum, 'make_freeforall')
        self.setFolderLocalRoles(forum,
                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
                                              {'id':'%s.members'%room_id,'roles':['Contributor','Editor',]},
                                              {'id':'%s.membersAdv'%room_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                              {'id':'%s.coordinators'%room_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},])
        return forum
    
    def createBlog(self):
        room_id=self.context.getId()
        blog_id=self.context.invokeFactory(id="blog",
                                   type_name='Blog',
                                   title="Blog")
        if not blog_id:
            return
        blog=self.context.restrictedTraverse(blog_id)
        self.setFolderLocalRoles(blog,
                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
                                              {'id':'%s.members'%room_id,'roles':['Contributor','Editor',]},
                                              {'id':'%s.membersAdv'%room_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                              {'id':'%s.coordinators'%room_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},])
        return blog
    
#    def createProject(self):
#        room_id=self.context.getId()
#        project_id=self.context.invokeFactory(id="progetto-%s" %room_id,
#                                              type_name='Project',
#                                              title="Progetto %s" %self.context.Title())
#        if not project_id:
#            return
#        project=self.context.restrictedTraverse(project_id)
#        self.setFolderLocalRoles(project,
#                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
#                                              {'id':'%s.members'%room_id,'roles':['Contributor','Editor',]},
#                                              {'id':'%s.membersAdv'%room_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
#                                              {'id':'%s.coordinators'%room_id,'roles':['LocalManager','Reader']},])
#        return project
    
    def createAreas(self):
        base_id= self.context.getId()
        self.blog=self.createBlog()
        documents=self.createArea(id='documenti',
                                  title='Documenti',
                                  portal_type="DocumentsArea",
                                  types=['Document','File','Image','Folder'],
                                  groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                          {'id':'%s.members'%base_id,'roles':['Contributor','Editor',]},
                                          {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                          {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},]
                                  )
        events=self.createArea(id='eventi',
                               title='Eventi',
                               portal_type="EventsArea",
                               types=['Event'],
                               groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                       {'id':'%s.members'%base_id,'roles':['Contributor','Editor',]},
                                       {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                       {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},]
                               )
        self.forum=self.createForum()
        news=self.createArea(id='notizie',
                             title='Notizie',
                             portal_type="NewsArea",
                             types=['News Item'],
                             groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                     {'id':'%s.members'%base_id,'roles':['Reader']},
                                     {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                     {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},]
                             )
        projects=self.createArea(id='progetti',
                                 title='Progetti',
                                 portal_type="ProjectsArea",
                                 types=['Project'],
                                 groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                         {'id':'%s.members'%base_id,'roles':['Contributor','Editor','Employee']},
                                         {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Reviewer','Employee']},
                                         {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Projectmanager','Contributor','Editor','EditorAdv','Reviewer']},]
                                 )
        polls=self.createArea(id='sondaggi',
                              title='Sondaggi',
                              portal_type="PollsArea",
                              types=['PlonePopoll'],
                              groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                      {'id':'%s.members'%base_id,'roles':['Contributor','Editor',]},
                                      {'id':'%s.membersAdv'%base_id,'roles':['Contributor','Editor','EditorAdv','Reviewer']},
                                      {'id':'%s.coordinators'%base_id,'roles':['LocalManager','Contributor','Editor','EditorAdv','Reviewer']},]
                              )
        
        return {'documents':documents,'events':events,'news':news,'projects':projects,'polls':polls}
        
    def createArea(self,id,title,portal_type,types=[],collection=False,groups=[]):
        """
        Create a folder with the given parameters
        """
        folder_id=self.context.invokeFactory(id=id,
                                             type_name=portal_type,
                                             title=title)
        area_obj=self.context.restrictedTraverse(folder_id)
        self.setFolderLocalRoles(area_obj,groups)
        if not types and not collection:
            return
        if portal_type=='NewsArea':
            self.createTopic(folder=area_obj,
                             id=id,
                             title=title,
                             portal_types=types,
                             portlet_manager='collective.portletpage.firstcolumn',
                             portletpage_index=2)
        elif portal_type=='DocumentsArea':
            self.createTopic(folder=area_obj,
                             id=id,
                             title=title,
                             portal_types=["Page","File","Image"],
                             portlet_manager='collective.portletpage.firstcolumn',
                             portletpage_index=1)
        elif portal_type=='EventsArea':
            self.createTopic(folder=area_obj,
                             id=id,
                             sort_on="start",
                             title=title,
                             portal_types=types,
                             portlet_manager='collective.portletpage.firstcolumn',
                             portletpage_index=3)
            
        elif portal_type=='PollsArea':
            self.createTopic(folder=area_obj,
                             id=id,
                             title=title,
                             portal_types=types,
                             portlet_manager='collective.portletpage.secondcolumn',
                             portletpage_index=4)
        
        elif portal_type=='ProjectsArea':
            self.createTopic(folder=area_obj,
                             id=id,
                             title=title,
                             portal_types=types,
                             portlet_manager='collective.portletpage.firstcolumn',
                             portletpage_index=4)
            
        if types:
            area_obj.setConstrainTypesMode(1)
            area_obj.setLocallyAllowedTypes(types)
            area_obj.setImmediatelyAddableTypes(types)
        
        return area_obj
    
    def setFolderLocalRoles(self,folder,list_groups):
        """
        Set the local roles for a given folder
        """
        #block the inherit
        folder.__ac_local_roles_block__ = True
        #set the local roles
        for group in list_groups:
            folder.manage_addLocalRoles(group.get('id'),group.get('roles'))
        #reindex the security
        folder.reindexObjectSecurity()
        
    def createAreaTopics(self,folder,id,title,**kwargs):
        """
        Create a collection
        """
        #create the first topic for default view
        self.createTopic(folder,id,title,kwargs.get('portal_types',[]))
        title=title+" per portlet"
        id=id+"-per-portlet"
        if kwargs.get('create_collection_portlet',False):
            kwargs['portlet_id']=id
            kwargs['portlet_title']=title
        self.createTopic(folder,id,title,**kwargs)
        
    def createTopic(self,folder,id,title,**kwargs):
        """
        Create a collection
        """
        topic_id=folder.invokeFactory(id=id,
                                      type_name='Topic',
                                      title=title)
        topic=folder.restrictedTraverse(topic_id)
        path_crit=topic.addCriterion('path','ATPathCriterion')
        path_crit.setValue(folder.UID())
        path_crit.setRecurse(True)
        topic.setSortCriterion(kwargs.get('sort_on','modified'), True)

        #set topic as view of the folder
        folder.setDefaultPage(topic_id)
        
        #optional settings
        portal_types= kwargs.get('portal_types',[])
        if portal_types:   
            if "PlonePopoll" in portal_types:
                portal_types='label_popoll'
            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue(portal_types)
        if kwargs.get('review_state',''):
            state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
            state_crit.setValue(kwargs.get('review_state',''))
        
        limit=3
        if folder.portal_type == "DocumentsArea":
            limit=5
        if folder.portal_type == "ProjectsArea":
            title="Gestione progetti"
        #create collection portlet for room's homepage
        assignment=self.createCollectionPortlet(collection_path='/'.join(topic.getPhysicalPath()),
                                                limit=limit,
                                                portlet_title=title)
        self.createPortlet(assignment,
                           portlet_id=id,
                           portlet_manager=kwargs.get('portlet_manager',''),
                           portletpage_index=kwargs.get('portletpage_index',0))
            
            
    
    #THEN WE CREATE THE RULES FOR THE ROOM
    def createRules(self,rule_type,group_type,types_list):
        rule_title='%s-%s'%(self.context.getId(),rule_type)
        
        message_created=self.translation_service.translate(msgid='notify_msg_created',
                                                           default='${title} has been created or modified. You can click on the following link to see it.\n${url}',
                                                           domain="rer.groupware.room",
                                                           context=self.context)
        
        message_deleted=self.translation_service.translate(msgid='notify_msg_deleted',
                                                           default='${title} has been deleted.',
                                                           domain="rer.groupware.room",
                                                           context=self.context)
        if rule_type == 'ruleNewsEvents':
            subject_created=self.translation_service.translate(msgid='notify_subj_created_small',
                                                          default='New news or event has been created or modified',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_small',
                                                          default='News or event has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            self.createRule(rule_title="%s-modified" %rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notifyNewsEvents'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notifyNewsEvents'%self.context.getId(),
                            types_list=types_list,
                            message=message_deleted,
                            subject=subject_deleted)
            
        if rule_type == 'ruleDocs':
            subject_created=self.translation_service.translate(msgid='notify_subj_created_big',
                                                          default='New document has been created or modified',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_big',
                                                          default='Document has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            self.createRule(rule_title="%s-modified" %rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notifyDocs'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notifyDocs'%self.context.getId(),
                            types_list=types_list,
                            message=message_deleted,
                            subject=subject_deleted)
            
        
    def createRule(self,rule_title,rule_event,group,types_list,message,subject):
        #create the rule
        rule=Rule()
        rule.event=rule_event
        rule.title=rule_title
        #add the rule to rule's storage
        storage = getUtility(IRuleStorage)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, rule)] = rule
        #set the condition and add it to the rule
        condition=PortalTypeCondition()
        condition.check_types=types_list
        rule.conditions.append(condition)  
        #set the action and add it to the rule
        action=MailGroupAction()
        
        action.members = []
        action.source = None
        action.groups=[group]
        action.subject=subject
        action.message=message
        rule.actions.append(action)
        #assignment
        rule_id=rule.id.replace('++rule++','')
        assignable = IRuleAssignmentManager(self.context)
        assignable[rule_id] = RuleAssignment(rule_id)
        assignable[rule_id].bubbles=True
        get_assignments(storage[rule_id]).insert('/'.join(self.context.getPhysicalPath()))
        
        
    #METHODS TO POPULATE PORTLETPAGE
    def createCollectionPortlet(self,collection_path,limit,portlet_title):
        """
        imposta l'assignment per la collection portlet
        """
        fixed_path=collection_path.replace(self.root_path,'')
        assignment=CollectionAssignment(header=portlet_title,
                                        target_collection=fixed_path,
                                        show_dates=True,
                                        limit=limit,
                                        show_more=True)
        
        return assignment
    
    def createPortlet(self,assignment,portlet_id,portletpage_index,portlet_manager):
            """
            
            """
            manager = getUtility(IPortletManager, name=portlet_manager, context= self.portlet_page)
            mapping = getMultiAdapter((self.portlet_page, manager), IPortletAssignmentMapping)
            # get hold of the user dashboard manager
            mapping[portlet_id] = assignment
            self.portlet_page_order[portlet_manager][portletpage_index]=portlet_id
    
    def createProjectsPortlet(self):
        assignment=ProjectsAssignment()
        return assignment
        
    def createBlogPortlet(self):
        if not self.blog:
            return None
        blog_folder='/'.join(self.blog.getPhysicalPath())
        fixed_path=blog_folder.replace(self.root_path,'')
        assignment=BlogAssignment(portletTitle="Ultimi post nel blog",
                                  blogFolder=fixed_path,
                                  entries=3)
        return assignment
    
    
    def createDiscussionPortlet(self):
        assignment=DiscussionAssignment(portletTitle="Ultimi commenti",
                                        discussionFolder='/%s'%self.context.getId(),
                                        nDiscussions=3)
        return assignment
    
    def createForumPortlet(self):
        assignment=PloneboardAssignment(title="Discussioni del forum",
                                        forumPath='/%s'%self.context.getId(),
                                        count=3)
        return assignment
    
    def createPopollPortlet(self):
        assignment=PopollAssignment(selection_mode='subbranches',
                                        number_of_polls=3)
        return assignment
    
    def adjustPortletPage(self):
#        #create the projects portlet
#        projects_portlet_assignment=self.createProjectsPortlet()
#        self.createPortlet(projects_portlet_assignment, 'groupware-project-management', 1, 'collective.portletpage.firstcolumn')
        #create the blog portlet
        blog_portlet_assignment=self.createBlogPortlet()
        self.createPortlet(blog_portlet_assignment, 'last_blog_entries', 3, 'collective.portletpage.secondcolumn')
        #create the discuss portlet
        discuss_portlet_assignment=self.createDiscussionPortlet()
        self.createPortlet(discuss_portlet_assignment, 'last_discussions', 1, 'collective.portletpage.secondcolumn')
        #create the forum portlet
        forum_portlet_assignment=self.createForumPortlet()
        self.createPortlet(forum_portlet_assignment, 'last_forum_conversations', 2, 'collective.portletpage.secondcolumn')
        #create popoll portlet
#        popoll_portlet_assignment=self.createPopollPortlet()
#        self.createPortlet(popoll_portlet_assignment, 'last_polls', 4, 'collective.portletpage.secondcolumn')
        
        for portlet_manager in ['collective.portletpage.firstcolumn','collective.portletpage.secondcolumn']:
            manager = getUtility(IPortletManager, name=portlet_manager, context= self.portlet_page)
            mapping = getMultiAdapter((self.portlet_page, manager), IPortletAssignmentMapping)
            portlet_order=self.portlet_page_order[portlet_manager].keys()
            portlet_order.sort()
            new_order=[self.portlet_page_order[portlet_manager][x] for x in portlet_order]
            mapping.updateOrder(new_order)
        
