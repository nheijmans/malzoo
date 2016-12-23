#!/usr/bin/python
import os
import sys
import yara
from ConfigParser import SafeConfigParser

class Signatures:
    """ 
    The yara class offers the functionality to scan a file or to 
    generate a new index based on the rules in the rules location
    in the configuration file malzoo.conf
    """

    def scan(self, filename, rule=None):
        # Open configuration file and get yara rules location
        conf_parser = SafeConfigParser()
        conf_parser.read('config/malzoo.conf')
        rule_path = conf_parser.get('settings','yara_rules')
    
        if rule:
            rules_location='{0}/{1}'.format(rule_path,rule)
        else:
            rules_location = '{0}/{1}'.format(rule_path,'index.yara')
        
        # Compile the rules in the index.yara and find matches on the sample
        rules   = yara.compile(rules_location)
        matches = [str(rule) for rule in rules.match(filename) ] # List of the rules that match
        if len(matches) > 0:
            return ','.join(matches)
        else:
            return None
    
    def generate_index(self):
        config_location = 'config/malzoo.conf'
        print "Opening config file: " + config_location + " (1/3)"
        conf_parser = SafeConfigParser()
        conf_parser.read(config_location)
    
        rules_location = conf_parser.get('settings','yara_rules')
    
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
