#!/usr/bin/python
import os
import sys
import yara
from ConfigParser import SafeConfigParser

def yarascan(filename):
    # Open configuration file and get yara rules location
    conf_parser = SafeConfigParser()
    conf_parser.read('config/app.conf')

    rules_location = conf_parser.get('data_location','yara_rules')
    
    # Compile the rules in the index.yara and find matches on the sample
    rules   = yara.compile(rules_location + 'index.yara')
    matches = [str(rule) for rule in rules.match(filename) ] # List of the rules that match
    if len(matches) > 0:
        return ','.join(matches)
    else:
        return None
