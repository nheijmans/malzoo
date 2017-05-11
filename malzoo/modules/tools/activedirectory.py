"""
File is part of Malzoo

The AD tool will check for a department and landcode to add to the e-mail
analysis.

"""
import simpleldap
import json
from ConfigParser import SafeConfigParser

class ActiveDirectory:
    def __init__(self):
        config_location = 'config/malzoo.conf'
        self.conf = SafeConfigParser()
        self.conf.read(config_location)

    def authenticate(self):
        conn = simpleldap.Connection(self.conf.get('ad','adserver'))
        if not conn.authenticate(dn=self.conf.get('ad','username'), 
                                 password=self.conf.get('ad','password')):
            raise "Auth problem!"

        return conn


    def parse_memberof(self, data):
        try:
            country_code = None
            for group in data:
                split = group.split(',')
                if self.conf.get('ad','countryfield') in split:
                    country_code = split[-3].split('=')[1]
                    if len(country_code) <= 3:
                        break
        except Exception as e:
            print "Country code error", e
            country_code = None
        finally:
            return country_code

    def search(self, category, keyword):
        conn = self.authenticate()
        
        try:
            users = conn.search("("+self.conf.get('ad','search')+"({0}={1}*))".format(category, keyword), 
                                base_dn=self.conf.get('ad','basedn'),
                                attrs=self.conf.get('ad','fields').split())

            dump = json.dumps(users[0])
            jdata = json.loads(dump)
            if 'department' in jdata:
                department = str(jdata['department'][0])
            else:
                department = None

            if 'memberof' in jdata:
                country_code = self.parse_memberof(jdata['memberof'])
            else:
                country_code = None
        except Exception as e:
            print "Error with AD check.", e
            department = None
            country_code = None
        finally:
            return (department,country_code)
