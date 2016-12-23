#!/usr/bin/python
"""
Distributor checks the queue and decides were the data should go to next.
Workers can add hashes or files to the queue for services to search or analyze
and the distrbutor will facilitate in that by offering a central point.

In the future it will also make sure the samples are distributed to the corect
worker and workers are being started according to the amount of samples.
"""

from malzoo.common.abstract              import Distributor
from malzoo.modules.services.apis        import *
from malzoo.modules.tools.general_info   import GeneralInformation
from malzoo.modules.tools.database       import MongoDatabase
from malzoo.modules.tools.signatures	 import Signatures

class DistributeBot(Distributor):
    """
    The distributeBot wants to receive the following info in a dict: md5, file(path), tag
    """
    def distribute(self,sample):
        cuckoo    = CuckooService()
        viper     = ViperService()
        mongodb   = MongoDatabase()
        filename  = sample['filename']
        yarasigs  = Signatures()
        match = yarasigs.scan(sample['filename'], rule='unwanted.yara')
        
        if not match:
            if 'md5' in sample:
                if self.conf.get('settings','duplicatecheck') == 'viper':
                    known = viper.search({'md5':sample['md5']})
                elif self.conf.get('settings','duplicatecheck') == 'mongo':
                    known = mongodb.search({'md5':sample['md5']})
                else:
                    known = False
                
                if known:
                    return {'response':'known'}
                else:
                    general_info = GeneralInformation(sample['filename'])
                    ft           = general_info.get_filetype()

                    #Create a package that can be used to push sample to
                    #cuckoo and viper. push only if enabled in the config
                    package = {'tags':sample['tag'],'file':sample['filename']}
                    if self.conf.getboolean('viper','enabled'):
                        viper.submit(package)
                    if self.conf.getboolean('cuckoo','enabled') and ft[0:11] != 'Zip archive':
                        cuckoo.submit(package)

                    match = yarasigs.scan(sample['filename'])
                    #Determine to which worker the file is assigned based on the mime
                    if ft[0:35] == 'Composite Document File V2 Document':
                        self.doc_q.put(sample)
                        result = {'result':'success'}
                    elif ft[0:4] == 'PE32':
                        self.pe_q.put(sample)
                        result = {'result':'success'}
                    elif ft[0:11] == 'Zip archive' and match != 'java_archive':
                        self.zip_q.put(sample)
                        result = {'result':'success'}
                    else:
                        self.other_q.put(sample)
                        result = {'result':'success'}

                    return result
            else:
                return {'error':'No md5 given'}
        else:
            print filename, "is in the unwanted yara rule"
            return
