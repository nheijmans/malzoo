#!/usr/bin/python
"""
File is part of Malzoo

A tool that saves a in-memory object to a location on disk
with the aid of a tempfile.
"""

import tempfile

from hashlib import md5 as md5sum
from hashlib import sha1 as sha1sum
from time    import time

class SaveObject:
    def save(self, obj, filename, tag, dist_q):
        data = dict()
        try:
            #Create a temporary file object and write to it
            temp = tempfile.TemporaryFile()
            temp.write(obj)
            temp.seek(0)
            
            #Hash the file in the file object
            md5_hash = md5sum(temp.read()).hexdigest()
            temp.seek(0)
            sha1_hash = sha1sum(temp.read()).hexdigest()
            temp.close()
            
            #Write the attached file to objs folder
            open('attachments/'+md5_hash,'wb').write(obj)
            
            #Send saved file to MalZoo,Cuckoo and Viper
            sample = dict()
            sample['md5']       = md5_hash
            sample['tag']    = tag
            sample['filename']  = 'attachments/'+md5_hash
            dist_q.put(sample)

            #Setup data dict for return
            data['id_tag']      = tag
            data['md5']         = md5_hash
            data['sha1']        = sha1_hash
            data['filename']    = filename
            data['submit_date'] = int(time())
        except Exception as e:
            print "SaveObject: Error on obj saving",e
            pass
        finally:
            return data
