#!/usr/bin/python
"""
Distributor checks the queue and decides were the data should go to next.
Workers can add hashes or files to the queue for services to search or analyze
and the distrbutor will facilitate in that by offering a central point.

In the future it will also make sure the samples are distributed to the corect
worker and workers are being started according to the amount of samples.
"""

from malzoo.common.abstract           import Distributor
from malzoo.core.services.apis        import *
from malzoo.core.tools.general_info   import GeneralInformation
from malzoo.core.tools.database       import MongoDatabase
from malzoo.core.tools.signatures     import Signatures

class DistributeBot(Distributor):
    """
    The distributeBot wants to receive the following info in a dict: md5, file(path), tag
    """
    def distribute(self,sample):
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
                    self.log('distributor - {0} - already in db'.format(sample['md5']))
                else:
                    general_info = GeneralInformation(sample['filename'])
                    ft           = general_info.get_filetype()

                    package = {'tags':sample['tag'],'file':sample['filename']}
                    if self.conf.getboolean('viper','enabled'):
                        viper.submit(package)

                    #determine to which worker the file is assigned based on the mime
                    match = yarasigs.scan(sample['filename'], rule='filetypes.yara')
                    if match == 'office_docs':
                        self.doc_q.put(sample)
                    elif match == 'executable':
                        self.pe_q.put(sample)
                    elif ft == 'application/zip' and match != 'java_archive':
                        self.zip_q.put(sample)
                    else:
                        self.other_q.put(sample)

                    #add the package to the modules for custom operations
                    self.mod_q.put(sample)
            else:
                self.log('distributor - {0} - no md5 given'.format(filename))
        else:
            self.log('distributor - {0} - matched with yara unwanted signature'.format(filename))

        return
