#!/usr/bin/python
"""
File is part of Malzoo

This tool works on forwarded e-mail text and extracts the beginning
e-mail text. This is being used to create a original e-mail object.
"""
import email
import re

class EmailToolkit:
    def is_forwarded(self, subject, body):
        """ Check if the e-mail is forwarded """
        is_fwd = False
        split  = re.split('\nFrom:|\nVan:', body)
        if subject[0:3].lower() == 'fw:' and len(split) >= 2:
            is_fwd = True
        return is_fwd

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
