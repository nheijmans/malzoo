#!/usr/bin/python
"""
File is part of Malzoo

The monitor function checks every five seconds for new samples in the directory.
It keeps track of the previous folder state so malware samples are not processed twice.
It adds the samples to the Queue that is shared with the workers.
"""
from Queue        import Queue
from time         import sleep
from os           import listdir

class Monitor:
    def __init__(self, dist_q):
        self.dist_q = dist_q

    def directory(self, path, tag=None):
        print "Directory monitor started on:",path
        before  = [f for f in listdir(path)]
    
        while True:
            sleep(5)
            files = listdir(path)
            if len(files) >= 0:
                after   = [f for f in listdir(path)]
                added   = [f for f in after if not f in before]
                
                for i in added:
                    if i[-4:] != '.tmp':
                        sample = {
                                  'file':i.split(':')[0],
                                  'tag':i.split(':')[1]
                                 }
                        self.dist_q.put(path+i)
                before = after
