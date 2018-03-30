"""
Module to submit samples to Cuckoo Sandbox for dynamic analysis. The response is captured with the
task ID but it does not do anything with it. 
"""

from malzoo.common.abstract import CustomModule

class CuckooSandbox(CustomModule):
    name = 'cuckoo'
    version = '0.1'
    enabled = False

    def submit(self, data):
        url   = 'http://<ip_here>:<port_here>/tasks/create/file'
        try:
            files = dict(file=open(data['file'], 'rb'))
            response = requests.post(url, files=files,timeout=5.0)
            response = json.dumps(response.text)
            response = json.loads(response)
        except requests.ConnectionError as e:
            self.log('{0} - {1} - {2}'.format('custom module',self.name,e))
        finally:
            return 

    def run(self):
        try:
            print self.name, 'is running'
            self.submit(self.pkg)
        except Exception as e:
            self.log('{0} - {1} - {2}'.format('custom module',self.name,e))
        finally:
            return

    
