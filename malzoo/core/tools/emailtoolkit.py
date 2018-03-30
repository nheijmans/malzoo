#!/usr/bin/python
"""
File is part of Malzoo

This tool works on forwarded e-mail text and extracts the beginning
e-mail text. This is being used to create a original e-mail object.
"""
import email
import re
from email.parser import HeaderParser
from email.header import decode_header
from malzoo.core.tools.saveobject import SaveObject

class EmailToolkit:
    def fwd_parser(self, subject, text):
        """ Parse the text to create a new EML """
        split = re.split('\nFrom:|\nVan:', text)
        raw = "From:"+split[-1]
        eml = email.message_from_string(raw)
        eml['subject'] = subject.strip('FW').strip('FWD').strip(':').strip()
    
        if eml['To'] == None:
            raw = 'From:'+split[-2]
            tmp = email.message_from_string(raw)
            eml['To'] = tmp['From']
        return eml

    def get_details(self, Email):
        """ 
        Return the receiver/sender information of a email message
        """
        details = None
    
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
    
                details = {
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
                    if details['to'] != None:
                        details['to'] = details['to'].split('<')[1].strip('>')
                        details['to'] = details['to'].split('>')[0]
                    
                    if details['from'] != None:
                        details['from'] = details['from'].split('<')[1].strip('>')
                        details['from'] = details['from'].split('>')[0]
                except:
                    pass

            except Exception as e:
                print "get_details error:", e
        finally:
            return details 
    
    def get_headers(self, Email):
        headers = None
        try:
            parser      = HeaderParser()
            raw_headers = parser.parsestr(Email.as_string())
            #headers     = dict()
            headers     = ""
            for key,value in raw_headers.items():
#                headers[str(key).lower()] = str(value).lower()
                headers += str(key).lower()+": "+str(value).lower()+"|"
        except Exception as e:
            print "Emailtoolkit: headers error",e
        finally:
            return headers

    def parse_attachment(self, attachment, msg_id, filename, tag, dist_q):
        """
        Parse the attachments from the e-mails and share the results
        """
        data = dict()
        try:
            saveobj = SaveObject()
            data = saveobj.save(attachment, filename, tag, dist_q)
            data['msg_id']      = msg_id
            data['sample_type'] = 'attachment'
        except Exception as e:
            print "Emailtoolkit: Error on attachment parsing", e
        finally:
            return data

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
    
