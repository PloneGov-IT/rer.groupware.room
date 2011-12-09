# -*- coding: utf-8 -*-
from rer.groupware.room import roomMessageFactory as _
from Products.CMFCore.utils import getToolByName

def sendNotificationOnModify(obj,event):
    portal=obj.portal_url.getPortalObject()
    pquickinstaller = getToolByName(portal, 'portal_quickinstaller')
    installed_products = pquickinstaller.listInstalledProducts()
    GPWRoomFound=False
    for p in installed_products:
        if p['title'] == u'RER: Groupware Room':
            GPWRoomFound = True
            break
    if not GPWRoomFound:
        return
    notify_newsevents=['News Item','Event']
    notify_docs=['Document','File','Image','Collection']
    room=None
    for element in obj.aq_chain:
        if getattr(element,'portal_type','') == "GroupRoom":
            room=element
    if not room:
        #the item isn't created in a room, and there is nothing to do
        return
    if obj.portal_type in notify_newsevents:
        sendMail(obj,room=room,group_type='notifyNewsEvents')
    elif obj.portal_type in notify_docs:
        sendMail(obj,room=room,group_type='notifyDocs')
    else:
        return

def sendMail(obj,room,group_type):
    """
    Send a mail to notification group
    """
    portal = obj.portal_url.getPortalObject()
    putils=getToolByName(portal, "plone_utils")
    portal_types=getToolByName(portal, "portal_types")
    translation_service=getToolByName(portal, "translation_service")
    sender_mail=portal.email_from_address
    sender_name=portal.email_from_name
    if not sender_mail:
        message=_('server_not_set',default=u'Impossible sending the notification. Mailserver not set in the portal.')
        putils.addPortalMessage(message, type='error')
        return
    group_id="%s.%s" %(room.getId(),group_type)
    dest=getEmailDest(portal,group_id)
    encoding = portal.getProperty('email_charset')
    mail_template=portal.restrictedTraverse('modified_mail_template')
    if not mail_template:
        message=_('mailtemplate_not_set',default=u'Impossible sending the notification. Mail template not set.')
        return
    friendly_type=portal_types.getTypeInfo(obj.portal_type).Title()
    mail_text = mail_template(mfrom="%s <%s>" %(sender_name,sender_mail),
                              mto=dest,
                              item=obj,
                              item_type=translation_service.utranslate(msgid=friendly_type,domain='plone',context=obj),   
                              charset=encoding,
                              request=obj.REQUEST)
    try:
        host = portal.MailHost
        host.send(mail_text.encode(encoding))
        obj.plone_log(_(u"Edit notify email sent to users"))
        
    except Exception, err:
        msg_text=_(u'Impossible sending the message: ')
        obj.plone_log(msg_text+ err[0])

def getEmailDest(portal,group_id):
    acl_users = getToolByName(portal, 'acl_users')
    group=acl_users.getGroupById(group_id)
    if not group:
        return ''
    mto=[]
    members=group.getGroupMembers()
    for member in members:
        if member.getProperty('email',''):
            mto.append(member.getProperty('email'))
    if mto:
        return ','.join(mto)
    else: 
        return ''