#!/usr/bin/python
import os
import sys
import logging
from shutil import move
from hashes import Hasher
from ConfigParser import SafeConfigParser

def add_to_repository(sample):
    conf_parser = SafeConfigParser()
    conf_parser.read('config/malzoo.conf')
    SAMPLE_DIR = conf_parser.get('settings','repository')
     
    hasher      = Hasher(sample)
    md5         = hasher.get_md5()
    archive_dir = SAMPLE_DIR+md5[:4]
    if os.path.exists(archive_dir) == False:
        os.makedirs(archive_dir)

    try:
        move(sample, archive_dir+'/'+md5)
        success = True
    except Exception, e:
        print e
        success = False
    finally:
        return success
