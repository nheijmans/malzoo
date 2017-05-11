#!/usr/bin/python
"""
The parent class Worker.
"""
#Default imports
from time               import sleep, time
from ConfigParser       import SafeConfigParser
from multiprocessing    import Process
import  logging

#MalZoo imports
from malzoo.modules.tools.database import MongoDatabase
from malzoo.modules.tools.storager import add_to_repository
from malzoo.modules.tools.logger   import dbg_logger
from malzoo.modules.tools.logger   import add_data as txtlog
from malzoo.modules.tools.splunk   import add_data as splunkie
from malzoo.modules.tools.es       import add_data as elastic
from malzoo.modules.tools.hashes   import Hasher


class Worker(Process):
    def __init__(self, sample_q, dist_q):
        super(Worker, self).__init__()
        self.sample_q   = sample_q
        self.dist_q = dist_q
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')

    def process(self):
        pass

    def share_data(self, data):
        mongodb  = MongoDatabase()
        if self.conf.getboolean('splunk','enabled'):
            splunkie(data)
        if self.conf.getboolean('mongo','enabled'):
            mongodb.add_sample(data)
        if self.conf.getboolean('elasticsearch','enabled'):
            elastic(data)
        if self.conf.getboolean('settings','textlog'):
            txtlog(data)

        return

    def store_sample(self, sample):
        if self.conf.getboolean('settings','storesample'):
            add_to_repository(sample)
        return

    def log(self, data):
        if self.conf.getboolean('settings','debug'):
            dbg_logger(data)
        return

    def run(self):
        while True:
            if self.sample_q.empty():
                sleep(5)
            else:
                sampleq     = self.sample_q.get()
                sample      = sampleq['filename']
                tag         = sampleq['tag']

                self.process(sample, tag)

class Supplier(Process):
    def __init__(self):
        super(Supplier, self).__init__()

    def log(self,data):
        if self.conf.getboolean('settings','debug'):
            dbg_logger(data)
        return

class Distributor(Process):
    def __init__(self,dist_q,pe_q,doc_q,zip_q,other_q):
        super(Distributor, self).__init__()
        #Configuration file
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')
        
        #Sample queues
        self.other_q = other_q
        self.dist_q  = dist_q
        self.doc_q   = doc_q
        self.zip_q   = zip_q
        self.pe_q    = pe_q

    def distribute(self):
        pass

    def log(self,data):
        if self.conf.getboolean('settings','debug'):
            dbg_logger(data)
        return

    def run(self):
        while True:
            if self.dist_q.empty():
                sleep(5)
            else:
                task = self.dist_q.get()
                self.distribute(task)

class Service(object):
    def __init__(self):
        super(Service, self).__init__()
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')

    def submit(self):
        pass

    def share_data(self, data, index):
        mongodb = MongoDatabase()
        if self.conf.getboolean('splunk','enabled'):
            add_data(data)
        if self.conf.getboolean('mongo','enabled'):
            mongodb.add_sample(data)
        return

class Tool(object):
    def __init__(self):
        super(Tool, self).__init__()
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')

    def use(self):
        pass
