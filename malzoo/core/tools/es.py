#!/usr/bin/env python3
from configparser import ConfigParser
from elasticsearch import Elasticsearch

def add_data(data):
    try:
        config_location = 'config/malzoo.conf'
        conf = ConfigParser()
        conf.read(config_location)

        host = conf.get('elasticsearch', 'host')
        port = conf.get('elasticsearch', 'port')

        es = Elasticsearch("http://{}:{}".format(host, port))
        es.index(index=conf.get('elasticsearch', 'index'), document=data)
    except Exception as e:
        print("elasticsearch tool: error", e)
    finally:
        return
