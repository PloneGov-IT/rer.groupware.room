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
from redturtle.portlet.custom_collection.redturtle_custom_collection_portlet import \
    Assignment as CollectionAssignment
from zope.app.container.interfaces import IObjectRemovedEvent, INameChooser
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

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
        self.blog=self.createBlog()
        self.forum=self.createForum()
        self.project=self.createProject()
        self.folders=self.createFolders()
        
        #create the rules
        self.createRules(rule_type='ruleSmall',
                        group_type='notifySmall',
                        types_list=set(['News Item','Event']))
        self.createRules(rule_type='ruleBig',
                        group_type='notifyBig',
                        types_list=set(['Document','File','Image','Collection']))
        
        #set local roles of the room
        self.setFolderLocalRoles(self.context,
                                 list_groups=[{'id':self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.hosts'%self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.coordinators'%self.context.getId(),'roles':['Reader']},])
        
        self.adjustPortletPage()
        
    #WE CREATE THE PORTLETPAGE
    def createPortletPage(self):
        """
        @author: andrea cecchi
        Crea una portletpage di partenza, da assegnare come vista predefinita per la stanza
        """
        portletpage_id=self.context.invokeFactory(id="homepage-%s" %self.context.getId(),
                                                  type_name='Portlet Page',
                                                  show_dates=True,
                                                  title="Homepage %s" %self.context.Title())
        
        #imposta la portletpage come vista pedefinita della stanza
        self.context.setDefaultPage(portletpage_id)
        
        portletpage=self.context.restrictedTraverse(portletpage_id)
        portletpage.manage_addLocalRoles('%s.coordinators'%self.context.getId(),['Editor','EditorAdv'])
        return portletpage
    
    #FIRST WE CREATE THE GROUPS
    def createGroups(self):
        groups_tool=getToolByName(self.context,'portal_groups')
        room_id=self.context.getId()
        room_title=self.context.Title()
        room_group=groups_tool.addGroup(id=room_id,title=room_title)
        if not room_group:
            return
        groups_tool.getGroupById(room_id).setProperties(roomgroup=True)
        groups_tool.addGroup(id='%s.notifyBig' %room_id,title='%s notifyBig' %room_title)
        groups_tool.addGroup(id='%s.notifySmall' %room_id,title='%s notifySmall' %room_title)
        groups_tool.addGroup(id='%s.coordinators' %room_id,title='%s coordinators' %room_title)
        groups_tool.addGroup(id='%s.hosts'%room_id,title='%s hosts' %room_title)

    #THEN WE CREATE THE AREAS
    def createForum(self):
        room_id=self.context.getId()
        forum_id=self.context.invokeFactory(id="forum-%s" %room_id,
                                            type_name='PloneboardForum',
                                            title="Forum %s" %self.context.Title())
        if not forum_id:
            return
        forum=self.context.restrictedTraverse(forum_id)
        self.setFolderLocalRoles(forum,
                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
                                              {'id':room_id,'roles':['Contributor','Editor',]},
                                              {'id':'%s.coordinators'%room_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},])
        return forum
    
    def createBlog(self):
        room_id=self.context.getId()
        blog_id=self.context.invokeFactory(id="blog-%s" %room_id,
                                   type_name='Blog',
                                   title="Blog %s" %self.context.Title())
        if not blog_id:
            return
        blog=self.context.restrictedTraverse(blog_id)
        self.setFolderLocalRoles(blog,
                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
                                              {'id':room_id,'roles':['Contributor','Editor',]},
                                              {'id':'%s.coordinators'%room_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},])
        return blog
    
    def createProject(self):
        room_id=self.context.getId()
        project_id=self.context.invokeFactory(id="progetto-%s" %room_id,
                                              type_name='Project',
                                              title="Progetto %s" %self.context.Title())
        if not project_id:
            return
        project=self.context.restrictedTraverse(project_id)
        self.setFolderLocalRoles(project,
                                 list_groups=[{'id':"%s.hosts"%room_id,'roles':['Reader']},
                                              {'id':room_id,'roles':['Contributor','Editor']},
                                              {'id':'%s.coordinators'%room_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer','Projectmanager']},])
        return project
    
    def createFolders(self):
        base_id= self.context.getId()
        documents=self.createFolder(id='documenti',
                          title='Documenti',
                          types=['Document','File','Image','Folder'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor',]},
                                  {'id':'%s.coordinators'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        events=self.createFolder(id='eventi',
                          title='Eventi',
                          types=['Event'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor',]},
                                  {'id':'%s.coordinators'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        news=self.createFolder(id='news',
                          title='News',
                          types=['News Item'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Reader']},
                                  {'id':'%s.coordinators'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        polls=self.createFolder(id='sondaggi',
                          title='Sondaggi',
                          types=['PlonePopoll'],
                          collection=False,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor']},
                                  {'id':'%s.coordinators'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        
        return {'documents':documents,'events':events,'news':news,'polls':polls}
        
    def createFolder(self,id,title,types=[],collection=False,groups=[]):
        """
        Create a folder with the given parameters
        """
        folder_id=self.context.invokeFactory(id= id,
                                             type_name='Folder',
                                             title=title)
        folder_obj=self.context.restrictedTraverse(folder_id)
        self.setFolderLocalRoles(folder_obj,groups)
        if not types and not collection:
            return
        if collection:
            if id=='news':
                self.createTopic(folder=folder_obj,
                                 id="ultime-%s" %id,
                                 review_state='published',
                                 title="Ultime %s" %title,
                                 portal_type=["News Item"],
                                 portlet_manager='collective.portletpage.firstcolumn',
                                 portletpage_index=4)
            elif id=='documenti':
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s-in-bozza" %id,
                                 title="Ultimi %s in bozza" %title,
                                 review_state='visible',
                                 sort_on="modified",
                                 portal_type=["Page","File","Image"],
                                 portlet_manager='collective.portletpage.firstcolumn',
                                 portletpage_index=2)
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s-definitivi" %id,
                                 title="Ultimi %s definitivi" %title,
                                 review_state='published',
                                 portal_type=["Page","File","Image"],
                                 portlet_manager='collective.portletpage.secondcolumn',
                                 portletpage_index=2)
            else:
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s" %id,
                                 review_state='published',
                                 sort_on="start",
                                 title="Ultimi %s" %title,
                                 portal_type=["Event"],
                                 portlet_manager='collective.portletpage.firstcolumn',
                                 portletpage_index=3)
        if types:
            folder_obj.setConstrainTypesMode(1)
            folder_obj.setLocallyAllowedTypes(types)
#        if id == 'blog':
#            folder_obj.setLayout('blog_view')
        
        return folder_obj
    
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
        
    def createTopic(self,folder,id,title,review_state,portlet_manager,portletpage_index,sort_on="effective",portal_type=[]):
        """
        Create a collection
        """
        topic_id=folder.invokeFactory(id= id,
                                      type_name='Topic',
                                      title=title)
        topic=folder.restrictedTraverse(topic_id)
        if portal_type:
            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue(portal_type)
#        sort_crit = topic.addCriterion('effective','ATSortCriterion')
#        sort_crit.setReversed(True)
        path_crit=topic.addCriterion('path','ATPathCriterion')
        path_crit.setValue(folder.UID())
        state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
        state_crit.setValue(review_state)
        topic.setSortCriterion(sort_on, True)
        limit=5
        #set topic as view of the folder
        if folder.getId() in ['news','eventi']:
            folder.setDefaultPage(topic_id)
            limit=5
        
        #create collection portlet for room's homepage
        assignment=self.createCollectionPortlet(collection_path='/'.join(topic.getPhysicalPath()),
                                                limit=limit,
                                                date_type=sort_on,
                                                portlet_title=title)
        self.createPortlet(assignment,portlet_id=id,portlet_manager=portlet_manager,portletpage_index=portletpage_index)
    
    
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
        if rule_type == 'ruleSmall':
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
                            group='%s.notifySmall'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notifySmall'%self.context.getId(),
                            types_list=types_list,
                            message=message_deleted,
                            subject=subject_deleted)
            
        if rule_type == 'ruleBig':
            subject_created=self.translation_service.translate(msgid='notify_subj_created_big',
                                                          default='New document has been created',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_big',
                                                          default='Document has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            self.createRule(rule_title="%s-modified" %rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notifyBig'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notifyBig'%self.context.getId(),
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
    def createCollectionPortlet(self,collection_path,limit,portlet_title,date_type):
        """
        imposta l'assignment per la collection portlet
        """
        fixed_path=collection_path.replace(self.root_path,'')
        assignment=CollectionAssignment(header=portlet_title,
                                        target_collection=fixed_path,
                                        limit=limit,
                                        show_dates=True,
                                        date_type=date_type,
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
        assignment=PloneboardAssignment(title="Ultimi messaggi",
                                        forumPath='/%s'%self.context.getId(),
                                        count=3)
        return assignment
    
    def createPopollPortlet(self):
        assignment=PopollAssignment(selection_mode='subbranches',
                                        number_of_polls=3)
        return assignment
    
    def adjustPortletPage(self):
        #create the blog portlet
        blog_portlet_assignment=self.createBlogPortlet()
        self.createPortlet(blog_portlet_assignment, 'last_blog_entries', 1, 'collective.portletpage.firstcolumn')
        #create the discuss portlet
        discuss_portlet_assignment=self.createDiscussionPortlet()
        self.createPortlet(discuss_portlet_assignment, 'last_discussions', 1, 'collective.portletpage.secondcolumn')
        #create the forum portlet
        forum_portlet_assignment=self.createForumPortlet()
        self.createPortlet(forum_portlet_assignment, 'last_forum_conversations', 3, 'collective.portletpage.secondcolumn')
        #create popoll portlet
        popoll_portlet_assignment=self.createPopollPortlet()
        self.createPortlet(popoll_portlet_assignment, 'last_polls', 4, 'collective.portletpage.secondcolumn')
        
        for portlet_manager in ['collective.portletpage.firstcolumn','collective.portletpage.secondcolumn']:
            manager = getUtility(IPortletManager, name=portlet_manager, context= self.portlet_page)
            mapping = getMultiAdapter((self.portlet_page, manager), IPortletAssignmentMapping)
            portlet_order=self.portlet_page_order[portlet_manager].keys()
            portlet_order.sort()
            new_order=[self.portlet_page_order[portlet_manager][x] for x in portlet_order]
            mapping.updateOrder(new_order)
        
