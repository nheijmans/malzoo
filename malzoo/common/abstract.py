#!/usr/bin/python
"""
The parent class Worker.
"""
#Default imports
from time               import sleep, time
from ConfigParser       import SafeConfigParser
from multiprocessing    import Process
from threading          import Thread
import  logging

#MalZoo imports
from malzoo.core.tools.database import MongoDatabase
from malzoo.core.tools.storager import add_to_repository
from malzoo.core.tools.logger   import dbg_logger
from malzoo.core.tools.logger   import add_data as txtlog
from malzoo.core.tools.splunk   import add_data as splunkie
from malzoo.core.tools.es       import add_data as elastic
from malzoo.core.tools.hashes   import Hasher


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
                sample = self.sample_q.get()
                self.process(sample)

class Supplier(Process):
    def __init__(self):
        super(Supplier, self).__init__()

    def log(self,data):
        if self.conf.getboolean('settings','debug'):
            dbg_logger(data)
        return

class Distributor(Process):
    def __init__(self,dist_q,pe_q,doc_q,zip_q,other_q,mod_q):
        super(Distributor, self).__init__()
        #Configuration file
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')
        
        #Sample queues
        self.other_q = other_q
        self.dist_q  = dist_q
        self.doc_q   = doc_q
        self.zip_q   = zip_q
        self.mod_q   = mod_q
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

class CustomModule(Thread):
    def __init__(self, package):
        super(CustomModule, self).__init__()
        self.pkg = package
        self.conf = SafeConfigParser()
        self.conf.read('config/malzoo.conf')

    def log(self, data):
        if self.conf.getboolean('settings','debug'):
            dbg_logger(data)
        return

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

    def run():
        pass
