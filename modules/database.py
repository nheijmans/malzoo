#!/usr/bin/python
from pymongo import MongoClient
from ConfigParser import SafeConfigParser

class MongoDatabase:
    def __init__(self):
        conf_parser = SafeConfigParser()
        conf_parser.read('config/app.conf')
        client = MongoClient()
        conf_parser.get('data_location','repository_dir')
        self.db = client[conf_parser.get('db_settings','db')]
        self.collection = self.db[conf_parser.get('db_settings','collection')]

    def add_sample(self, data):
        try:
            object_id = self.collection.insert(data)
        except:
            print "Error: Could not insert into Mongo"
            pass

        return

    def find_hash(self, md5):
        collection = self.db.malware_samples
        result = collection.find_one({'md5':md5},{'md5':1, '_id':0})
        if result == None:
            return {'md5':'nothing'}

        else:
            return result
