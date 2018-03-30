#!/usr/bin/python
"""
File is part of Malzoo

The monitor function checks every 60 seconds for new samples in the directory.
It keeps track of the previous folder state so malware samples are not processed twice.
It adds the samples to the Queue that is shared with the workers.
"""
#Parent
from malzoo.common.abstract import Supplier

#Default library imports
from Queue        import Queue
from time         import sleep
from os           import listdir
from os.path      import isfile
from os.path      import isdir

# malzoo imports
from malzoo.core.tools.hashes       import Hasher

class Monitor(Supplier):
    def __init__(self, path, dist_q):
        self.path   = path
        self.dist_q = dist_q

        self.before = set()
        self.after  = set()

    def inventory(self, path):
        items = listdir(path)
        if len(items) >= 0:
            for item in items:
                i = '{0}/{1}'.format(path,item)
                if isfile(i): 
                    self.after.add(i)
                if isdir(i):
                    self.inventory(i)
        return

    def check(self, path):
        self.inventory(path)
        added   = [f for f in self.after if not f in self.before]
        for i in added:
            if i[-4:] != '.tmp':
                sample=dict()
                sample['filename'] = i
                sample['tag'] = 'dirmon'
                hashbot = Hasher(sample['filename'])
                sample['md5'] = hashbot.get_md5()
                self.dist_q.put(sample)
        self.before = self.after
        self.after  = set()

        return

    def run(self):
        while True:
            sleep(6)
            self.check(self.path)
        return
