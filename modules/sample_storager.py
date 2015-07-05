#!/usr/bin/python
import os
import sys
import logging
from shutil import move
from hashes import Hasher
from ConfigParser import SafeConfigParser

def add_to_repository(sample):
    conf_parser = SafeConfigParser()
    conf_parser.read('config/app.conf')
    SAMPLE_DIR = conf_parser.get('data_location','repository_dir')
     
    hasher = Hasher(sample)
    md5         = hasher.get_md5()
    archive_dir = SAMPLE_DIR+md5[:4]
    if os.path.exists(archive_dir) == False:
        os.makedirs(archive_dir)

    try:
        move(sample, archive_dir+'/'+md5)
        return True
    except Exception, e:
        print e
        return False

def main(dirs):
    LOG_FILE = 'log/storing_samples.log'
    logging.basicConfig(filename=LOG_FILE,
                        level=logging.DEBUG)

    for d in dirs:
        for sample in os.listdir(d):
            state = add_to_repository(d+"/"+sample)
            if state:
                logging.info('Sample stored: ' + sample)
            else:
                logging.error('Sample raised an error: ' + sample)

    print "[+] Job completed, have a nice day!"
