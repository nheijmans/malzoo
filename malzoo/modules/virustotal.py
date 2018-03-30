"""
Simple MalZoo module to search samples to VirusTotal and print the results of samples.

*** WARNING *** Watch your API Calls! *** WARNING ***

"""

from malzoo.common.abstract import CustomModule
import requests
import json

class VirusTotal(CustomModule):
    # Malzoo required fields
    name = 'virustotal'
    version = '0.1'
    enabled = False

    # VT required fields
    api_key  = "your-api-key-here"
    base_url = "https://www.virustotal.com/vtapi/v2/file/report"

    def get_result(self,a):
        for k,v in a.items():
            print k,':',v

        payload  = {'resource':a['md5'], 'apikey':self.api_key}
        response = requests.get(self.base_url, params=payload, timeout=5.0)
        jdata    = json.loads(response.text)
        print "virustotal",jdata
    
        if jdata['response_code'] == 1:
            print "got results"
        else:
            print "not yet in VT"
        
        return

    def run(self):
        try:
            print self.name, 'is running'
            self.get_result(self.pkg)
            self.share_data("text")
        except Exception as e:
            print "vt",e
            self.log('{0} - {1} - {2}'.format('custom module',self.name,e))
        finally:
            return

    
