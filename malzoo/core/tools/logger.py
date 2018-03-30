#!/usr/bin/python
import json
import logging
from ConfigParser import SafeConfigParser

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

    return l

def add_data(data):
    try:
        logger = logging.getLogger('analysis')
        logger.info(data)

    except Exception as e:
        print "txtlogger, error",e
    finally:
        return

def dbg_logger(data):
    try:
        logger = logging.getLogger('debug')
        logger.info(data)

    except Exception as e:
        print "debug logger, error",e
    finally:
        return
