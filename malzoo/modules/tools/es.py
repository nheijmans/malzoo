#!/usr/bin/python
from ConfigParser import SafeConfigParser
from elasticsearch import Elasticsearch

def add_data(data):
    try:
        config_location = 'config/malzoo.conf'
        conf = SafeConfigParser()
        conf.read(config_location)

        es = Elasticsearch([{'host': conf.get('elasticsearch','host'), 
                             'port': conf.get('elasticsearch','port')}])

	es.index(index=conf.get('elasticsearch','index'), doc_type='event', body=data)
    except Exception as e:
        print "elasticsearch tool: error",e
    finally:
        return
