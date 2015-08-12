#!/usr/bin/python
"""
MalZoo is a mass malware repository script that is connected to a Mongo database
to store information of a PE file. With the information collected by MalZoo you can
search for related malware and see trends in your malware collection as you grow
your zoo. 

Date: 12/08/2015
Version: 1.2
Author: Niels Heijmans
License: GPL 1.0

"""
# Module imports
import os
import sys
import time
import magic
import argparse
from ConfigParser import SafeConfigParser
from modules.worker import do_work
from modules.yara_index import create_yara_index
from modules.watchdog import watchdog
from multiprocessing import Process, Queue

# Argument definition
parser = argparse.ArgumentParser()
parser.add_argument('-t','--tag', action='store', dest='tag', 
           help='Assign this tag in Mongo to the samples')

parser.add_argument('-d', action='store', dest='directory', 
           help='Directory with the malware samples (run app once)')

parser.add_argument('-y','--update-yara', action='store_true', default=False,
           dest='yara', help='Updates the YARA index')

parser.add_argument('-w','--watchdog', action='store', dest='watchdog', 
            help='Watch a folder for new files to process')

# Execution
if __name__ == '__main__':
    conf_parser = SafeConfigParser()
    conf_parser.read('config/app.conf')
    options = parser.parse_args()

    if options.tag and options.directory and not options.watchdog:
        nr_processes = 8
        samples = os.listdir(options.directory)
        samples_list = [options.directory + '/' + sample + ":" + options.tag for sample in samples]
        sample_queue = Queue()

        # Filling up the queue with samples
        for sample in samples_list:
            sample_queue.put(sample)

        print "[+] You are about to start MalZoo and collect information. "
        print "[*] please check if everyhing is correct: "  
        print "[*] Path to samples: ", options.directory 
        print "[*] No. of samples: ", str(sample_queue.qsize())
        print "[*] No. of threads to use: ", str(nr_processes) 
        print "[*] The tag to identify this set:", options.tag  
        y_n = raw_input("[!] Is this correct? [y/n]: ")
        check = y_n.lower()

        if check == 'y' or check == 'yes':
            print "\n[*] Starting the analysis:"
            try:
                # Setup the threads for analysis
                jobs = []
                for i in range(nr_processes):
                    p = Process(target=do_work, args=(sample_queue,i,))
                    p.daemon = True
                    jobs.append(p)

                for job in jobs:
                    job.start()

                while True:
                    if sample_queue.empty():
                        break
                    else:
                        time.sleep(5)

                for job in jobs:
                    job.terminate()

                print "[+] Done with analysis!"

            except Exception, e:
                print "[!] Error thingie: ", e
                pass

        elif check == 'n' or check == 'no':
            print "[-] The operation is cancelled."
            sys.exit()
    
    elif options.tag and options.watchdog and not options.directory: 
        nr_processes = 8 
        sample_queue = Queue()

        try:
            # Setup the watchdog
            wp = Process(target=watchdog, args=(sample_queue, options.watchdog, options.tag,))
            wp.daemon = True
            wp.start()

            # Setup the threads for analysis
            for i in range(nr_processes):
                p = Process(target=do_work, args=(sample_queue,i,))
                p.daemon = True
                p.start()

            wp.join() 

        except Exception, e:
            print "[!] Error thingie: ", e
            pass

    elif options.yara:
        print "[*] Updating YARA index..."
        create_yara_index()
        print "[+] Done!"

    else:
        print "[!] The -t(tag) is mandatory in combination with -w(watchdog) or -d(directory)! You cannot use both at the same time"
