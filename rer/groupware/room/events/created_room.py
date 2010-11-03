# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility,queryUtility
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.conditions.portaltype import PortalTypeCondition
from zope.app.container.interfaces import IObjectRemovedEvent,INameChooser
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from collective.contentrules.mailtogroup.actions.mail import MailGroupAction
from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.app.contentrules.rule import get_assignments
from redturtle.portlet.custom_collection.redturtle_custom_collection_portlet import Assignment as CollectionAssignment
from plone.portlets.interfaces import IPortletManager, IPortletAssignment, IPortletAssignmentMapping

class CreateRoomStructure(object):

    def __init__(self, context, event):
        """
        @author: andrea cecchi
        
        """
        self.context = context
        self.translation_service=getToolByName(self.context,'translation_service')
        self.portlet_page = self.createPortletPage()
        self.createGroups()
        self.createForum()
#        self.createBlog()
        self.createFolders()
        self.createRules(rule_type='ruleSmall',
                        group_type='notificheSmall',
                        types_list=set(['News Item','Event']))
        self.createRules(rule_type='ruleBig',
                        group_type='notificheBig',
                        types_list=set(['Document','File','Image','Collection']))
        
        self.setFolderLocalRoles(self.context,
                                 list_groups=[{'id':self.context.getId(),'roles':['Contributor','Editor','Reader']},
                                              {'id':'%s.hosts'%self.context.getId(),'roles':['Reader']},
                                              {'id':'%s.coordinator'%self.context.getId(),'roles':['EditorAdv','LocalManager','Contributor','Editor','Reader','Reviewer']},])
        
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
        return self.context.restrictedTraverse(portletpage_id)
    
    def createCollectionPortlet(self,collection_path,portlet_title,date_type):
        """
        imposta l'assignment per la collection portlet
        """
        assignment=CollectionAssignment(header=portlet_title,
                                        target_collection=collection_path,
                                        limit=3,
                                        show_dates=True,
                                        date_type=date_type,
                                        show_more=True)
        
        return assignment
    
    def createPortlet(self,assignment,portlet_id,portlet_manager):
            """
            
            """
            manager = getUtility(IPortletManager, name=portlet_manager, context= self.portlet_page)
            mapping = getMultiAdapter((self.portlet_page, manager), IPortletAssignmentMapping)
    
            # get hold of the user dashboard manager
            mapping[portlet_id] = assignment
            
            
    #FIRST WE CREATE THE GROUPS
    def createGroups(self):
        groups_tool=getToolByName(self.context,'portal_groups')
        room_id=self.context.getId()
        room_title=self.context.Title()
        room_group=groups_tool.addGroup(id=room_id,title=room_title)
        if not room_group:
            return
        groups_tool.getGroupById(room_id).setProperties(roomgroup=True)
        groups_tool.addGroup(id='%s.notificheBig'%room_id)
        groups_tool.addGroup(id='%s.notificheSmall'%room_id)
        groups_tool.addGroup(id='%s.coordinator'%room_id)
        groups_tool.addGroup(id='%s.hosts'%room_id)

    #THEN WE CREATE THE AREAS
    def createForum(self):
        self.context.invokeFactory(id="forum-%s" %self.context.getId(),
                                   type_name='PloneboardForum',
                                   title="Forum %s" %self.context.Title())
                   
    def createBlog(self):
        self.context.invokeFactory(id="blog-%s" %self.context.getId(),
                                   type_name='Weblog',
                                   title="Blog %s" %self.context.Title())
    
    def createFolders(self):
        base_id= self.context.getId()
        self.createFolder(id='documenti',
                          title='Documenti',
                          types=['Document','File','Image','Folder'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor',]},
                                  {'id':'%s.coordinator'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        self.createFolder(id='eventi',
                          title='Eventi',
                          types=['Event'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor',]},
                                  {'id':'%s.coordinator'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        self.createFolder(id='news',
                          title='News',
                          types=['News Item'],
                          collection=True,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Reader']},
                                  {'id':'%s.coordinator'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        self.createFolder(id='sondaggi',
                          title='Sondaggi',
                          types=['PlonePopoll'],
                          collection=False,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor']},
                                  {'id':'%s.coordinator'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        self.createFolder(id='blog',
                          title='Blog',
                          types=['Document'],
                          collection=False,
                          groups=[{'id':"%s.hosts"%base_id,'roles':['Reader']},
                                  {'id':base_id,'roles':['Contributor','Editor']},
                                  {'id':'%s.coordinator'%base_id,'roles':['EditorAdv','LocalManager','Contributor','Editor','Reviewer']},]
                          )
        
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
                                 portlet_manager='collective.portletpage.firstcolumn')
            elif id=='documenti':
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s-in-bozza" %id,
                                 title="Ultimi %s in bozza" %title,
                                 review_state='visible',
                                 sort_on="modified",
                                 portal_type=["Page","File","Image"],
                                 portlet_manager='collective.portletpage.firstcolumn')
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s-definitivi" %id,
                                 title="Ultimi %s definitivi" %title,
                                 review_state='published',
                                 portal_type=["Page","File","Image"],
                                 portlet_manager='collective.portletpage.secondcolumn')
            else:
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s" %id,
                                 review_state='published',
                                 sort_on="start",
                                 title="Ultimi %s" %title,
                                 portal_type=["Event"],
                                 portlet_manager='collective.portletpage.firstcolumn')
        if types:
            folder_obj.setConstrainTypesMode(1)
            folder_obj.setLocallyAllowedTypes(types)
        if id == 'blog':
            folder_obj.setLayout('blog_view')
    
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
        
    def createTopic(self,folder,id,title,review_state,portlet_manager,sort_on="effective",portal_type=[]):
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
        assignment=self.createCollectionPortlet(collection_path='/'.join(topic.getPhysicalPath()),
                                                date_type=sort_on,
                                                portlet_title=title)
        self.createPortlet(assignment,portlet_id=id,portlet_manager=portlet_manager)
    
    
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
                                                          default='rer.groupware small notifications: new news or event has been created or modified',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_small',
                                                          default='rer.groupware small notifications: news or event has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            self.createRule(rule_title="%s-modified" %rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notificheSmall'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notificheSmall'%self.context.getId(),
                            types_list=types_list,
                            message=message_deleted,
                            subject=subject_deleted)
            
        if rule_type == 'ruleBig':
            subject_created=self.translation_service.translate(msgid='notify_subj_created_big',
                                                          default='rer.groupware big notifications: new object has been created',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_big',
                                                          default='rer.groupware big notifications: object has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            self.createRule(rule_title="%s-modified" %rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notificheBig'%self.context.getId(),
                            types_list=types_list,
                            message=message_created,
                            subject=subject_created)
            
            self.createRule(rule_title="%s-removed" %rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notificheBig'%self.context.getId(),
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
        
        
    #AND AT LEAST WE CREATE THE LAST PORTLETS FOR THE ROOM'S HOMEPAGE
    