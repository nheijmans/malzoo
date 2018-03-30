#!/usr/bin/python
"""
File is part of Malzoo

This service gives access to the API's of MalZoo, Viper and Cuckoo.
It makes it possible to submit samples to the specified service.

For now the classes are in one file, if they get expanded too far they might
be splitted in the future to seperate services.
"""

#Default library imports
import requests
import json

#MalZoo imports
from malzoo.common.abstract import Service

class MalzooService(Service):
    def submit(self, data):
        url = 'http://{0}:{1}/file/add'.format(self.conf.get('malzoo','host'), 
                                                self.conf.get('malzoo','port'))
        payload = {'tag':data['tags']}
        files = dict(file=open(data['filename'], 'rb'))
        try:
            response = requests.post(url, files=files, data=payload)
            response = json.dumps(response.text)
            response = json.loads(response)
            return response
        except requests.ConnectionError:
            return{'error':
                    'Unable to connect to MalZoo API at "{0}".'.format(url)}

class ViperService(Service):
    def search(self, sample):
        url     = 'http://{0}:{1}/file/find'.format(self.conf.get('viper','host'), 
                                                self.conf.get('viper','port'))
        payload = sample
        try:
            response = requests.post(url, data=payload)
            response = json.dumps(response.text)
            response = json.loads(response)
            if '../' in response:
                reply = False
            else:
                reply = True
        except requests.ConnectionError:
            reply =  {'error':
                    'Unable to connect to Viper API at "{0}".'.format(url)}
        finally:
            return reply

    def submit(self, sample):
        url     = 'http://{0}:{1}/file/add'.format(self.conf.get('viper','host'), 
                                                self.conf.get('viper','port'))
        payload = {'tags':sample['tags']}
        files = dict(file=open(sample['file'], 'rb'))
        try:
            response = requests.post(url, files=files, data=payload)
            response = json.dumps(response.text)
            response = json.loads(response)
        except requests.ConnectionError:
            response =  {'error':
                    'Unable to connect to Viper API at "{0}".'.format(url)}
        finally:
            return response
