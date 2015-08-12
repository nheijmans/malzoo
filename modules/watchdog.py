#!/usr/bin/python
"""
The watchdog function checks every five seconds for new samples in the directory.
It keeps track of the previous folder state so malware samples are not processed twice.
It adds the samples to the Queue that is shared with the workers. The workers check the
queue every two seconds for new samples. 
"""
from Queue      import Queue
from time       import sleep
from os         import listdir

def watchdog(q, path, tag):
    before  = [f for f in listdir(path)]

    while True:
        sleep(5)
        files = listdir(path)
        if len(files) >= 0:
            after   = [f for f in listdir(path)]
            added   = [f for f in after if not f in before]
            
            for i in added:
                q.put(path+i+':'+tag)

            before = after

        print "Watchdog: Qsize is %s" % q.qsize()
