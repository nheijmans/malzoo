#!/usr/bin/python
"""
File is part of Malzoo

In this module the databases that are supported can be used by the workers
to add samples. For now only Mongo is supported.
"""
from pymongo import MongoClient
from ConfigParser import SafeConfigParser

class MongoDatabase:
    def __init__(self):
        conf_parser = SafeConfigParser()
        conf_parser.read('config/malzoo.conf')

        client = MongoClient()
        self.db         = client[conf_parser.get('mongo','db')]
        self.collection = self.db[conf_parser.get('mongo','collection')]

    def add_sample(self, data):
        try:
            object_id = self.collection.insert(data)
        except:
            print "Error: Could not insert into Mongo"
            pass
        
        finally:
            return

    def search(self, md5):
        collection  = self.db.malware_samples
        result      = self.collection.find_one({'md5':md5['md5']},{'md5':1, '_id':0})
        if result == None:
            return False
        else:
            return True
