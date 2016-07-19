"""
File is part of Malzoo

IMAP supplier. Attempts to get all e-mails from the account defined in the configuration and 
add them to the emailworker queue.
"""
import re
import os
import sys # temporary to catch keyboard error
import time
import email
import imaplib
import ConfigParser

from multiprocessing import Process, Queue

class Imap:
    def open_connection(self, verbose=False):
        """
        Setup the IMAP connection with the server
        in the configuration file
        """
        # Connect to the server
        hostname = self.conf.get('imap', 'server')
        if verbose: print 'Connecting to', hostname
        connection = imaplib.IMAP4_SSL(hostname)
    
        # Login to our account
        username = self.conf.get('imap', 'username')
        password = self.conf.get('imap', 'password')
        if verbose: print 'Logging in as', username
        connection.login(username, password)
        return connection
    
    def list_mailboxes(self):
        """ Retrieve all folders and subfolders """
        try:
            #c = self.open_connection()
            c = self.c
            response_code, data = c.list()
        except Exception as e:
            print e
        finally:
            #c.logout()
            return data
    
    def get_ids(self, mailbox):
        """ 
        Get all messages from the given folder and return the ID numbers 
        """
        #c = self.open_connection()
        c = self.c
        msg_ids = []
        try:
            response, data = c.select(mailbox,readonly=True)
            num_msgs = int(data[0])
            response, msg_ids = c.search(None, '(UNSEEN)')
    
        finally:
            #c.close()
            #c.logout()
            return msg_ids
    
    def fetch_mail(self, mailbox, batch_ids):
        """ 
        For each mail ID, fetch the whole email and parse it with msgparser 
        """
        try:
            #c = self.open_connection()
            c = self.c
            response, data = c.select(mailbox)
            response, messages = c.fetch(batch_ids,"(RFC822)")
        except Exception as e:
            messages = None
            print e
        finally:
            #c.close()
            #c.logout()
            return messages
    
    def copy_message(self, mailbox, ID, target):
        """ Copy a message to the target folder """
        success = False
        try:
            #c = self.open_connection()
            c = self.c
            response, data = c.select(mailbox)
            c.copy(ID,target)
            success = True
        finally:
            #c.close()
            #c.logout()
            return success
        
    def move_message(self, mailbox, ID, target):
        """ Move a message to the target folder """
        success = False
        try:
            #c = self.open_connection()
            c = self.c
            response, data = c.select(mailbox)
            c.copy(ID,target)
            c.store(ID, '+FLAGS', '\\Deleted')
            success = True
        finally:
            #c.close()
            #c.logout()
            return success

    def run(self, mail_q):
        """ Start the process """
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('config/malzoo.conf')

        # 1. List all mailboxes available
#        directories = self.list_mailboxes()                    
        mailbox     = self.conf.get('imap','folder')

        while True:
            try:
                self.c = self.open_connection()
                connected = True
            except Exception as e:
                print time.localtime(), "Can't connect!"
                print e
                connected = False
            
            if connected:
                try:
            # 2. Get ID's from new messages in mailbox INBOX
                    email_ids   = self.get_ids(mailbox)     
    
                    if email_ids[0] != '': 
                        batch_ids   = ','.join(email_ids[0].split())
    
            # 3. Get the messages from defined mailbox and the list of ID's
                        emails      = self.fetch_mail(mailbox, batch_ids)
                        if emails != None:
                            for i in range(0,len(emails),2):
                                email = {'filename':emails[i][1],'tag':self.conf.get('settings','tag')}
                                mail_q.put(email)
                        else:
                            print "Emails could not be fetched"
    
            # 4. Check again in 10 seconds
                    self.c.close()
                    self.c.logout()
                    time.sleep(60) 
    
                except KeyboardInterrupt:
                    sys.exit(0)
            else:
                time.sleep(120)
