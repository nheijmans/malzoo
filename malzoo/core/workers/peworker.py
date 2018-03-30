#!/usr/bin/python
"""
This is the worker that will be executed per sample of the Portable Executable filetype. 
It collects the information of the sample via different tools.
"""
#Parent
from malzoo.common.abstract import Worker

#Imports 
from time                              import time
from malzoo.core.tools.signatures   import Signatures
from malzoo.core.tools.hashes       import Hasher
from malzoo.core.tools.strings      import strings
from malzoo.core.tools.general_info import GeneralInformation
from malzoo.core.tools.pe           import PeInfo

class PEWorker(Worker):
    def process(self, sample):
        """ This function will process the PE files """
        try:
            # Create objects from the classes
            hasher       = Hasher(sample['filename'])
            general_info = GeneralInformation(sample['filename'])
            pe_info      = PeInfo(sample['filename'], 'data/userdb.txt')
            sigs_yara    = Signatures()
    
            # Get basic info
            ft      = general_info.get_filetype()
    
            if (pe_info.packer_detect() != None or  
               pe_info.packer_detect != [] or  
               pe_info.packer_detect != "N.A."):
                strings_sample = strings(sample['filename'])
            else:
                strings_sample = "Packer detected"
    
            # Creating a dictionary with sample information
            sample_info = { 
            'filename'          : general_info.get_filename(),
            'filetype'          : general_info.get_filetype(),
            'filesize'          : str(general_info.get_filesize()),
            'md5'               : hasher.get_md5(),
            'sha1'              : hasher.get_sha1(),
            'pehash'            : hasher.get_pehash(),
            'imphash'           : hasher.get_imphash(),
            'fuzzy'             : hasher.get_fuzzy(),
            'yara_results'      : sigs_yara.scan(sample['filename']),
            'pe_compiletime'    : pe_info.get_compiletime(),
            'pe_dll'            : pe_info.get_dll(),
            'pe_packer'         : pe_info.packer_detect(),
            'pe_language'       : pe_info.get_language(),
            'original_filename' : pe_info.get_org_filename(),
            'submit_date'       : int(time()),
            'sample_type'       : 'exe',
            'id_tag'            : sample['tag']
            }
    
            self.share_data(sample_info)
            self.store_sample(sample['filename'])
        except Exception, e:
            self.log('{0} - {1} - {2} '.format('peworker',sample,e))
        finally:
            return
