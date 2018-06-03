#!/usr/bin/python
import json
import requests
from ConfigParser import SafeConfigParser
from time         import time

def add_data(data):
    try:
        config_location = 'config/malzoo.conf'
        conf = SafeConfigParser()
        conf.read(config_location)
        url = 'https://{0}:{1}/services/collector'.format(conf.get('splunk','host'),
                conf.get('splunk','port'))
        header = {'Authorization':conf.get('splunk','token')}
        post_data = {
                      'time':int(time()),
                      'host':conf.get('splunk','host'),
                      'sourcetype':conf.get('splunk','sourcetype'),
                      'event':data
                    }
        log_data = json.dumps(post_data).encode('utf8')
        r = requests.post(url, headers=header, data=log_data, verify=False)
    except Exception as e:
        print "test, error",e
    finally:
        return
