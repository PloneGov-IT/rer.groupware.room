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
from plone.portlet.collection.collection import Assignment as CollectionAssignment
from plone.portlets.interfaces import IPortletManager, IPortletAssignment, IPortletAssignmentMapping

class CreateRoomStructure(object):

    def __init__(self, context, event):
        """
        @author: andrea cecchi
        
        """
        self.context = context
        self.translation_service=getToolByName(self.context,'translation_service')
        self.portlet_page = self.createPortletPage()
        self.createForum()
        self.createGroups()
        self.createFolders()
        self.createRules(rule_type='ruleSmall',
                        group_type='notificheSmall',
                        types_list=set(['News Item','Event']))
        self.createRules(rule_type='ruleBig',
                        group_type='notificheBig',
                        types_list=set(['Document','File','Image','Collection']))
    
    def createPortletPage(self):
        portletpage_id=self.context.invokeFactory(id="homepage-%s" %self.context.getId(),
                                                  type_name='Portlet Page',
                                                  show_dates=True,
                                                  title="Homepage %s" %self.context.Title())
        
        #imposta la portletpage come vista pedefinita della stanza
        if self.context.hasProperty('default_page'):
            self.context._updateProperty("default_page",portletpage_id)
        else:
            self.context._setProperty("default_page",portletpage_id)
        return self.context.restrictedTraverse(portletpage_id)
     
    def createForum(self):
        self.context.invokeFactory(id="forum-%s" %self.context.getId(),
                                   type_name='PloneboardForum',
                                   title="Forum %s" %self.context.Title())
                   
    def createCollectionPortlet(self,collection_path,portlet_title):
        """
        imposta l'assignment per la collection portlet
        """
        assignment=CollectionAssignment(header=portlet_title,
                                         target_collection=collection_path,
                                         limit=5,
                                         show_more=True)
        
        return assignment
    
    def createPortlet(self,assignment,portlet_id):
            """
            
            """
            manager_name = 'collective.portletpage.firstcolumn'
            manager = getUtility(IPortletManager, name=manager_name, context= self.portlet_page)
            mapping = getMultiAdapter((self.portlet_page, manager), IPortletAssignmentMapping)
    
            # get hold of the user dashboard manager
            mapping[portlet_id] = assignment
    
    def createFolders(self):
        self.createFolder(id='news',title='News',types=['News Item'],collection=True)
        self.createFolder(id='eventi',title='Eventi',types=['Event'],collection=True)
        self.createFolder(id='documenti',title='Documenti',types=['Document','File','Image','Folder'],collection=False)
        self.createFolder(id='sondaggi',title='Sondaggi',types=['PlonePopoll'],collection=False)
        
    def createFolder(self,id,title,types=[],collection=False):
        folder_id=self.context.invokeFactory(id= id,
                                             type_name='Folder',
                                             title=title)
        folder_obj=self.context.restrictedTraverse(folder_id)
        self.setFolderLocalRoles(folder_obj,folder_id)
        if not types and not collection:
            return
        if collection:
            if id=='news':
                self.createTopic(folder=folder_obj,
                                 id="ultime-%s" %id,
                                 title="Ultime %s" %title,
                                 portal_type=["News Item"])
            else:
                self.createTopic(folder=folder_obj,
                                 id="ultimi-%s" %id,
                                 title="Ultimi %s" %title,
                                 portal_type=["Event"])
        if types:
            folder_obj.setConstrainTypesMode(1)
            folder_obj.setLocallyAllowedTypes(types)
    
    def setFolderLocalRoles(self,folder,folder_id):
        group_id=self.context.getId()
        #block the inherit
        folder.__ac_local_roles_block__ = True
        #set the local roles
        folder.manage_addLocalRoles(group_id,['Reader'])
        if folder_id == 'news':
            folder.manage_addLocalRoles("%s.coordinator"%group_id,['EditorAdv','LocalManager','Contributor','Editor','Reader'])
        if folder_id in ['eventi','documenti']:
            folder.manage_addLocalRoles(group_id,['Contributor','Editor','Reader'])
            folder.manage_addLocalRoles("%s.coordinator"%group_id,['EditorAdv','LocalManager','Contributor','Editor','Reader'])
        #reindex the security
        folder.reindexObjectSecurity()
        
    def createTopic(self,folder,id,title,portal_type=[]):
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
        state_crit.setValue('published')
        topic.setSortCriterion('effective', True)
        assignment=self.createCollectionPortlet(collection_path='/'.join(topic.getPhysicalPath()),
                                                portlet_title=title)
        self.createPortlet(assignment,portlet_id=id)
        
    def createGroups(self):
        groups_tool=getToolByName(self.context,'portal_groups')
        room_id=self.context.getId()
        room_title=self.context.Title()
        room_group=groups_tool.addGroup(id=room_id,title=room_title)
        if not room_group:
            return
        
        groups_tool.getGroupById(room_id).setProperties(roomgroup=True)
        #groups_tool.setRolesForGroup(room_id,['Contributor','Editor'])
        groups_tool.addGroup(id='%s.notificheBig'%room_id)
        groups_tool.addGroup(id='%s.notificheSmall'%room_id)
        groups_tool.addGroup(id='%s.coordinator'%room_id)
#        groups_tool.setRolesForGroup('%s.coordinator'%room_id,['EditorAdv','LocalManager','Contributor','Editor'])
        groups_tool.addGroup(id='%s.hosts'%room_id)
#        groups_tool.setRolesForGroup('%s.hosts'%room_id,['Reader'])
    
    
    def createRules(self,rule_type,group_type,types_list):
        rule_title='%s-%s'%(self.context.getId(),rule_type)
        if rule_type == 'ruleSmall':
            subject_created=self.translation_service.translate(msgid='notify_subj_created_small',
                                                          default='rer.groupware small notifications: new news or event has been created',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            subject_deleted=self.translation_service.translate(msgid='notify_subj_deleted_small',
                                                          default='rer.groupware small notifications: news or event has been deleted',
                                                          domain="rer.groupware.room",
                                                          context=self.context)
            
            self.createRule(rule_title=rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notificheSmall'%self.context.getId(),
                            types_list=types_list,
                            subject=subject_created)
            
            self.createRule(rule_title=rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notificheSmall'%self.context.getId(),
                            types_list=types_list,
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
            
            self.createRule(rule_title=rule_title,
                            rule_event=IObjectModifiedEvent,
                            group='%s.notificheBig'%self.context.getId(),
                            types_list=types_list,
                            subject=subject_created)
            
            self.createRule(rule_title=rule_title,
                            rule_event=IObjectRemovedEvent,
                            group='%s.notificheBig'%self.context.getId(),
                            types_list=types_list,
                            subject=subject_deleted)
            
        
    def createRule(self,rule_title,rule_event,group,types_list,subject):
        #create the rule
        rule=Rule()
        rule.event=rule_event
        rule.title=rule_title
        #add the rule to rule's storage
        storage = getUtility(IRuleStorage)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, rule)] = rule
    #    #set the condition and add it to the rule
        condition=PortalTypeCondition()
        condition.check_types=types_list
        rule.conditions.append(condition)  
    #    #set the action and add it to the rule
        action=MailGroupAction()
        
        action.members = []
        action.source = None
        action.groups=[group]
        action.subject=subject
        action.message=self.translation_service.translate(msgid='notify_text',
                                                     default='${title} has been created. You can click on the following link to see it.\n${url}',
                                                     domain="rer.groupware.room",
                                                     context=self.context)
        rule.actions.append(action)
    #    #assignment
        rule_id=rule.id.replace('++rule++','')
        assignable = IRuleAssignmentManager(self.context)
        assignable[rule_id] = RuleAssignment(rule_id)
        assignable[rule_id].bubbles=True
        get_assignments(storage[rule_id]).insert('/'.join(self.context.getPhysicalPath()))