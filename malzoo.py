#!/usr/bin/python
"""
MalZoo is a mass malware repository script that is connected to a Mongo database
to store information of malware samples. With the information collected by 
MalZoo you can search for related malware and see trends in your malware 
collection as you grow your zoo. 

Date: 19/07/2016
Version: 2.0
Author: Niels Heijmans
License: GPL 2.0

"""
#Default modules
import os
import sys
import time
import argparse
from ConfigParser                          import SafeConfigParser
from multiprocessing                       import Process, Queue

#Suppliers of samples
from malzoo.modules.suppliers.monitor      import Monitor
from malzoo.modules.suppliers.imap         import Imap
from malzoo.modules.suppliers.api          import WebApi

#Sample workers
from malzoo.modules.workers.emailworker    import EmailWorker
from malzoo.modules.workers.otherworker    import OtherWorker
from malzoo.modules.workers.docworker      import OfficeWorker
from malzoo.modules.workers.zipworker      import ZipWorker
from malzoo.modules.workers.peworker       import PEWorker

#Services
from malzoo.modules.services.distributor   import DistributeBot

#Tools
from malzoo.modules.tools.signatures       import Signatures
from malzoo.modules.tools.logger           import setup_logger

# Argument definition
parser = argparse.ArgumentParser(description='Malzoo: Automated Static Malware Analysis', version='Malzoo-v2.0')
parser.add_argument('-u','--update-yara', action='store_true', default=False,
           dest='yara', help='Update the YARA index')


# Execution
if __name__ == '__main__':
    conf = SafeConfigParser()
    conf.read('config/malzoo.conf')

    options      = parser.parse_args()
    pe_queue     = Queue()
    doc_queue    = Queue()
    zip_queue    = Queue()
    dist_queue   = Queue()
    mail_queue   = Queue()
    other_queue  = Queue()
    nr_processes = int(conf.get('settings','nr_workers'))

    # Option --yara-update
    if options.yara:
        print "[*] Updating YARA index..."
        sigs_yara = Signatures()
        sigs_yara.generate_index()
        print "[+] Done!"
    else:
        try:
            print "[*] Malzoo wil run in monitor mode now!" 
            print "[*] Starting components..."
            suppliers = []
            workers   = []
            services  = []

            a_logger = setup_logger('analysis','logs/analysis_results.log')
            d_logger = setup_logger('debug','logs/debug.log')

            # Starting suppliers, if enabled in the configuration file
            if conf.getboolean('suppliers','api'):
                print "[+] Starting API supplier!"
                ap = Process(target=WebApi, args=(dist_queue,))
                ap.daemon = True
                ap.start()
                suppliers.append(ap)

            if conf.getboolean('suppliers','mail'):
                print "[+] Starting mail supplier!"
                imap = Imap()
                mp = Process(target=imap.run, args=(mail_queue,))
                mp.daemon = True
                mp.start()
                suppliers.append(mp)

            if conf.getboolean('suppliers','dir'):
                print "[+] Starting Directory monitor!"
                monitor = Monitor(conf.get('settings','dirmonitor'),dist_queue)
                monitor.daemon = True
                monitor.run()
                suppliers.append(monitor)

            # Starting workers
            #Portable Executables
            for i in range(4):
                p = PEWorker(pe_queue, dist_queue)
                p.daemon = True
                p.start()
                workers.append(p)

            #Office
            for i in range(nr_processes):
                p = OfficeWorker(doc_queue, dist_queue)
                p.daemon = True
                p.start()
                workers.append(p)

            #Email
            for i in range(nr_processes):
                p = EmailWorker(mail_queue, dist_queue)
                p.daemon = True
                p.start()
                workers.append(p)

            #ZIP
            for i in range(nr_processes):
                p = ZipWorker(zip_queue, dist_queue)
                p.daemon = True
                p.start()
                workers.append(p)

            #Other
            for i in range(nr_processes):
                p = OtherWorker(other_queue, dist_queue)
                p.daemon = True
                p.start()
                workers.append(p)

            #Starting Distributor
            for i in range(3):
                d = DistributeBot(dist_queue, pe_queue, doc_queue, zip_queue, other_queue)
                d.daemon = True
                d.start()
                services.append(d)

            for supplier in suppliers:
                supplier.join()

        except KeyboardInterrupt:
            for worker in workers:
                worker.terminate()
            for supplier in suppliers:
                supplier.terminate()
            for service in services:
                service.terminate()
            print "[*] Thanks for using MalZoo!"

        finally:
            sys.exit()
