#!/usr/bin/python
"""
This scripts is made to create a index for all yara rules in the directory
specified in the configuration file app.conf
"""
# Imports
import os
import yara
from ConfigParser import SafeConfigParser


def create_yara_index():
    config_location = 'config/app.conf'
    print "Opening config file: " + config_location + " (1/3)"
    conf_parser = SafeConfigParser()
    conf_parser.read(config_location)

    rules_location = conf_parser.get('data_location','yara_rules')

    print "Opening file index.yar in " + rules_location + "(2/3)"
    with open(rules_location + 'index.yara', 'w') as rules_index:
        for rule_file in os.listdir(rules_location):
            # Skip rules with wrong extension
            if not rule_file.endswith('.yar') and not rule_file.endswith('.yara'):
                continue
    
            # Skip if it's the index itself.
            if rule_file == 'index.yara':
                continue
    
            # Add the rule to the index.
            line = 'include "{0}"\n'.format(rule_file)
            rules_index.write(line)

    print "Adding rules to index.yar and writing the file (3/3)"
