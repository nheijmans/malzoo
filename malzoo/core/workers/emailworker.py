#!/usr/bin/python
"""
File is part of Malzoo

E-mail/MSG Parser.
This parser handles email objects and extracts information from them that can
be stored (e.g. header and body). It also saves attachments in emails to a
folder and pushes these to Cuckoo and Viper.
"""

#Parent
from malzoo.common.abstract import Worker

#Default Imports
import os
import re
import email
import base64
import olefile
import requests
from hashlib import md5 as md5sum
from hashlib import sha1 as sha1sum
from time import time

#Malzoo imports
from malzoo.core.tools.hashes           import Hasher
from malzoo.core.tools.activedirectory  import ActiveDirectory
from malzoo.core.tools.emailtoolkit     import EmailToolkit
from malzoo.core.tools.urlextractor     import get_urls

class EmailWorker(Worker):
    def process(self, Email, tag="api"):
        """ 
        Parse each email and extract attachment(s) 
        """
        try:
            etk = EmailToolkit()
            #Variables for adding data
            original_mail   = False
            has_attachments = False
            attached_files  = []
    
            #If the supplied email is a string, make it a Email object
            if isinstance(Email, str):
                msg = email.message_from_string(Email)
            else:
                msg = Email
    
            #Get details and get the attachments
            mail_info   = etk.get_details(msg)
            attachments = msg.get_payload()
            mail_info['headers'] = etk.get_headers(msg)
    
            #No attachments, only the body of the e-mail
            if isinstance(attachments, str):
                if mail_info['encoding'] == 'base64':
                    attachments = base64.decodestring(attachments)

                mail_info['attachments'] = has_attachments
                mail_info['submit_date'] = int(time())
                mail_info['sample_type'] = 'email'
                self.share_data(mail_info)

                #Check the body for links
                urls = get_urls(attachments)
                if urls != None:
                    for url in set(urls):
                        url_info = {}
                        url_info['url']         = url
                        url_info['msg_id']      = mail_info['msg_id']
                        url_info['sample_type'] = 'url'
                        self.share_data(url_info)
    
            # Multiple attachments found, process each and act accordingly
            else:
                for obj in attachments:
                    content_type = obj.get_content_type() 
                    filename     = obj.get_filename()
    
                    #If the filename is set, write the attachment to a subfolder
                    if filename:
                        #Decode the file
                        file_attachment = obj.get_payload(decode=True)
                        has_attachments = True
    
                        #Use the function parse_attachment to save the file
                        sample = etk.parse_attachment(file_attachment, mail_info['msg_id'], filename, tag, self.dist_q)
                        self.share_data(sample)
    
                    elif content_type == 'text/html':
                        body = obj.get_payload(decode=True)
                        urls = get_urls(body)
                        pass

                    elif content_type == 'text/plain':
                        body = obj.get_payload()
                        urls = get_urls(body)
                        body.strip()
                        mail_info['body'] = body
                            
                    elif content_type == 'multipart/related':
                        pass

                    #If the attachment is another e-mail, process this
                    elif content_type == 'message/rfc822':
                        original_mail = True
                        mail_attachment = obj.get_payload(decode=False)
                        self.process(mail_attachment[0], tag)
                # If it is not the original e-mail but the attached MSG, share the data
                if not original_mail:
                    mail_info['attachments'] = has_attachments
                    mail_info['submit_date'] = int(time())
                    mail_info['sample_type'] = 'email'
                    self.share_data(mail_info)

                    if urls != None:
                        for url in set(urls):
                            url_info = {}
                            url_info['url']     = url
                            url_info['msg_id']  = mail_info['msg_id']
                            url_info['sample_type'] = 'url'
                            self.share_data(url_info)
        except Exception, e:
            self.log('{0} - {1} - {2} '.format('emailworker',sample,e))
        finally:
            return
