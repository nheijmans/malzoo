#!/usr/bin/python
"""
All filetypes that do not have a specified worker are being picked
up by this Worker. It will collect the general information and hashes
from it. 
"""
#Parent
from malzoo.common.abstract import Worker

#Imports
import magic

#Malzoo imports
from time import time
from malzoo.core.tools.general_info import GeneralInformation
from malzoo.core.tools.signatures   import Signatures
from malzoo.core.tools.hashes       import Hasher

class OtherWorker(Worker):
    def process(self, sample):
        try:
            hasher       = Hasher(sample['filename'])
            general_info = GeneralInformation(sample['filename'])
            sigs_yara    = Signatures()
            mymagic      = magic.Magic(mime=True)

            sample_info = { 
            'filename'          : general_info.get_filename(),
            'filetype'          : mymagic.from_file(sample['filename']),
            'filesize'          : str(general_info.get_filesize()),
            'md5'               : hasher.get_md5(),
            'sha1'              : hasher.get_sha1(),
            'yara_results'      : sigs_yara.scan(sample['filename']),
            'submit_date'       : int(time()),
            'sample_type'       : 'other',
            'id_tag'            : sample['tag']
            } 
            self.share_data(sample_info)
            self.store_sample(sample)
        except Exception, e:
            self.log('{0} - {1} - {2} '.format('otherworker',sample,e))
        finally:
            return


    
