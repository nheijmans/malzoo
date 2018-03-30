#!/usr/bin/python
"""
File is part of Malzoo

API supplier
"""
#Default library imports
import os
import time
import json
import magic
from bottle import request
from bottle import route
from bottle import run
from zipfile import ZipFile
from ConfigParser import SafeConfigParser

#Malzoo imports
from malzoo.core.tools.general_info import GeneralInformation
from malzoo.core.tools.hashes       import Hasher

def WebApi(dist_q):
    def jsonize(data):
        return json.dumps(data, sort_keys=False, indent=4)
    
    @route('/test')
    def test():
        return 'Test successful!\n'
    
    @route('/file/add', method='POST')
    def upload_file():
        upload_dir  = 'uploads/'
        tmp     = '.tmp'
        tag     = request.forms.get('tag')
        upload  = request.files.get('file')
        sample  = dict()

        if tag == None:
            tag = 'api'
    
        upload.filename = upload.filename
        if not os.path.exists(upload_dir+upload.filename):
            # Add the .tmp extension so it won't be processed right away by monitoring services
            upload.save(upload_dir+upload.filename+tmp)
            time.sleep(1)
            os.rename(upload_dir+upload.filename+tmp, upload_dir+upload.filename)
            sample['filename'] = upload_dir+upload.filename
            sample['tag']  = tag

            hashbot       = Hasher(sample['filename'])
            sample['md5'] = hashbot.get_md5()

            dist_q.put(sample)
            return "File submitted for analysis!\n"
        else:
            return "Sample already in uploads directory!\n"
        
    def start_api():
        conf = SafeConfigParser()
        conf.read('config/malzoo.conf')
        run(host=conf.get('malzoo','host'), port=conf.get('malzoo','port'), quiet=True)

    start_api()
