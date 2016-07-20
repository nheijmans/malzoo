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
from email.header import decode_header
from hashlib import md5 as md5sum
from hashlib import sha1 as sha1sum
from time import time

#Malzoo imports
from malzoo.modules.tools.hashes           import Hasher
from malzoo.modules.tools.saveobject       import SaveObject
from malzoo.modules.tools.activedirectory  import ActiveDirectory
from malzoo.modules.tools.emailtoolkit     import EmailToolkit
from malzoo.modules.tools.urlextractor     import get_urls

class EmailWorker(Worker):
    def parse_ole_msg(self, ole):
        """
        Parse a OLE email and format it to a RFC822 email
        """
        stream_dirs = ole.listdir()
        for stream in stream_dirs:
            # get stream that contains the email header
            if stream[0].startswith('__substg1.0_007D'):
                email_header = ole.openstream(stream).read()
                if stream[0].endswith('001F'):  # Unicode probably needs something better than just stripping \x00
                    email_header = email_header.replace('\x00', '')
        # If it came from outlook we may need to trim some lines
        try:
            email_header = email_header.split('Version 2.0\x0d\x0a', 1)[1]
        except Exception as e:
            print "Emailworker: Ole error", e
            pass
    
        # Leaving us an RFC compliant email to parse
        msg = email.message_from_string(email_header)
        return msg
    
    def get_header(self, Email):
        """ 
        Return the receiver/sender information of a email message
        """
        header = None
    
        try:
            ole = olefile.OleFileIO(Email)
            ole_flag = True
            msg = self.parse_ole_msg(ole)
    
        except Exception as e:
            try:
                ole_flag = False
            
                if ole_flag:
                    msg = self.parse_ole_msg(ole)
                elif isinstance(Email, str):
                    msg = email.message_from_string(Email)
                else:
                    msg = Email
    
                header = {
                           'subject'    : str(decode_header(msg.get("Subject"))[0][0]),
                           'to'         : msg.get("To"),
                           'from'       : msg.get("From"),
                           'cc'         : msg.get("Cc"),
                           'bcc'        : msg.get("Bcc"),
                           'date'       : msg.get("Date"),
                           'encoding'   : msg.get("Content-Transfer-Encoding"),
                           'msg_id'     : msg.get("Message-ID")
                         }
                try:
                    if header['to'] != None:
                        header['to'] = header['to'].split('<')[1].strip('>')
                        header['to'] = header['to'].split('>')[0]
                    
                    if header['from'] != None:
                        header['from'] = header['from'].split('<')[1].strip('>')
                        header['from'] = header['from'].split('>')[0]
                except:
                    pass

            except Exception as e:
                print "get_header error:", e
        finally:
            return header
    
    def parse_attachment(self, attachment, msg_id, filename, tag):
        """
        Parse the attachments from the e-mails and share the results
        """
        data = dict()
        try:
            saveobj = SaveObject()
            data = saveobj.save(attachment, filename, tag, self.dist_q)
            data['msg_id']  = msg_id
            data['sample_type'] = 'attachment'
            self.share_data(data)
        except Exception as e:
            print "Emailworker: Error on attachment parsing", e
        finally:
            return data

    def ad_request(self, fromaddr, toaddr):
        """
        Uses the tool module activedirectory to get the reporters location 
        based on a search in the AD
        """
        ad = ActiveDirectory()
        try:
            REGEX = self.conf.get('workers','email_regex')
            mboxname = self.conf.get('workers','emailaddr')
            if fromaddr != None and fromaddr != mboxname and re.match(REGEX, fromaddr.lower()):
                re.match(REGEX, fromaddr)
                adresults = ad.search('mail',fromaddr)
            elif toaddr != None and toaddr != mboxname and re.match(REGEX, toaddr.lower()):
                adresults = ad.search('mail',toaddr)
            else:
                adresults = (None, None)
        except Exception as e:
            print "Emailworker: AD request error", e
            adresults = (None, None)
        finally:
            return adresults

    def process(self, Email, tag):
        """ 
        Parse each email and extract attachment(s) 
        """
	print "working on e-mail"
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
    
            #Get header and get the attachments
            mail_info   = self.get_header(msg)
            attachments = msg.get_payload()
    
            #No attachments, only the body of the e-mail
            if isinstance(attachments, str):
                if mail_info['encoding'] == 'base64':
                    attachments = base64.decodestring(attachments)

                if etk.is_forwarded(mail_info['subject'], attachments) == True:
                    result = etk.fwd_parser(subject, attachments)
                    mail_info['subject'] = result['subject']
                    mail_info['From']    = result['From']
                    mail_info['To']      = result['To']

                mail_info['attachments'] = has_attachments
                mail_info['submit_date'] = int(time())
                mail_info['sample_type']       = 'email'

                if self.conf.getboolean('ad','adlookup'):
                    adresults = self.ad_request(mail_info['from'], mail_info['to'])
                    mail_info['department']    = adresults[0]
                    mail_info['country_code']  = adresults[1]

                self.share_data(mail_info)

                #Check the body for links
                urls = get_urls(attachments)
                if urls != None:
                    for url in set(urls):
                        url_info = {}
                        url_info['url']     = url
                        url_info['msg_id']  = mail_info['msg_id']
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
                        sample = self.parse_attachment(file_attachment, mail_info['msg_id'], filename, tag)
    
                    elif content_type[0:4] == 'text':
                        try:
                            body = obj.get_payload(decode=True)
                            urls = get_urls(body)
                            
                        except Exception as e:
                            print "Emailworker: FW error subattachment",e

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

                    # !!! EXPERIMENTAL !!!
                    if self.conf.getboolean('ad','adlookup'):
                        adresults = self.ad_request(mail_info['from'], mail_info['to'])    
                        mail_info['department']   = adresults[0]
                        mail_info['country_code'] = adresults[1]
                        mail_info['sample_type']      = 'email'

                    self.share_data(mail_info)

                    if urls != None:
                        for url in set(urls):
                            url_info = {}
                            url_info['url']     = url
                            url_info['msg_id']  = mail_info['msg_id']
                            url_info['sample_type'] = 'url'
                            self.share_data(url_info)
        except Exception, e:
            print "Emailworker: Error on sample:",sample,e,"\n"
        finally:
            return
