"""
File is part of Malzoo

The AD tool will check for a department and landcode to add to the e-mail
analysis.

"""
import json
from ldap3 import Server, Connection, ALL
from configparser import ConfigParser

class ActiveDirectory:
    def __init__(self):
        config_location = 'config/malzoo.conf'
        self.conf = ConfigParser()
        self.conf.read(config_location)

    def authenticate(self):
        server = Server(self.conf.get('ad', 'adserver'), get_info=ALL)
        conn = Connection(server,
                          user=self.conf.get('ad', 'username'),
                          password=self.conf.get('ad', 'password'),
                          auto_bind=True)
        return conn

    def parse_memberof(self, data):
        try:
            country_code = None
            for group in data:
                split = group.split(',')
                if self.conf.get('ad', 'countryfield') in split:
                    country_code = split[-3].split('=')[1]
                    if len(country_code) <= 3:
                        break
        except Exception as e:
            print("Country code error", e)
            country_code = None
        finally:
            return country_code

    def search(self, category, keyword):
        conn = self.authenticate()

        try:
            search_filter = "(" + self.conf.get('ad', 'search') + "({0}={1}*))".format(category, keyword)
            base_dn = self.conf.get('ad', 'basedn')
            attrs = self.conf.get('ad', 'fields').split()

            conn.search(base_dn, search_filter, attributes=attrs)

            if not conn.entries:
                return (None, None)

            entry = json.loads(conn.entries[0].entry_to_json())['attributes']

            if 'department' in entry and entry['department']:
                department = str(entry['department'][0])
            else:
                department = None

            if 'memberOf' in entry and entry['memberOf']:
                country_code = self.parse_memberof(entry['memberOf'])
            else:
                country_code = None
        except Exception as e:
            print("Error with AD check.", e)
            department = None
            country_code = None
        finally:
            conn.unbind()
            return (department, country_code)
