#!/usr/bin/python
"""
Date: 24/04/2015
Version: 0.1
Author: nheijmans
License: GPL 2.0

"""
# Module imports
import os
import sys
import time
import magic
import argparse
from ConfigParser import SafeConfigParser
from modules.worker import do_work
from pymongo import MongoClient
from multiprocessing import Pool
from modules.yara_index import create_yara_index

def cron_run(directory, tag):
    no_cpu = int(16)
    pool = Pool(processes=no_cpu)
    samples = os.listdir(directory)
    samples_list = [directory + '/' + sample + ":" + tag for sample in samples]
    pool.map(do_work, samples_list) # Execute the data extraction


# Argument definition
parser = argparse.ArgumentParser()
parser.add_argument('-t','--tag', action='store', dest='tag', 
           help='Assign this tag in Mongo to the samples')

parser.add_argument('-d','--directory', action='store', dest='directory', 
           help='Directory with the malware samples')

parser.add_argument('-y','--update-yara', action='store_true', default=False,
           dest='yara', help='Updates the YARA index')

# Execution
if __name__ == '__main__':
    conf_parser = SafeConfigParser()
    conf_parser.read('config/app.conf')
    options = parser.parse_args()

    if options.tag and options.directory:
        no_cpu = int(conf_parser.get('cpu_cores','cores'))
        pool = Pool(processes=no_cpu)
        samples = os.listdir(options.directory)
        samples_list = [options.directory + '/' + sample + ":" + options.tag for sample in samples]

        print "[+] You are about to start ZooKeeper and collect information. "
        print "[*] please check if everyhing is correct: "  
        print "[*] Path to samples: ", options.directory 
        print "[*] No. of samples: ", str(len(samples_list)) 
        print "[*] No. of cores to use: ", str(no_cpu) 
        print "[*] The tag to identify this set:", options.tag  
        y_n = raw_input("[!] Is this correct? [y/n]: ")
        check = y_n.lower()

        if check == 'y' or check == 'yes':
            print "\n[*] Starting the analysis:"
            try:
                pool.map(do_work, samples_list) # Execute the data extraction
                print "\n[+] Done with analysis!"
            except Exception, e:
                print "[!] Error thingie: ", e
                pass

        elif check == 'n' or check == 'no':
            print "[-] The operation is cancelled."
            sys.exit()
    
    elif options.yara:
        print "[*] Updating YARA index..."
        create_yara_index()
        print "[+] Done!"


    else:
        print "[!] The -t(tag) and -d(directory) options are mandatory!"
	parser.print_help()
