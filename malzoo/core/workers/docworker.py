#!/usr/bin/python
"""
Microsoft Office document parser. 
"""
#Parent
from malzoo.common.abstract         import Worker

#Imports
import oletools.oleid
import magic
import json
import os
from time                           import sleep,time
from oletools.olevba                import VBA_Parser, VBA_Scanner

#Malzoo imports
from malzoo.core.tools.hashes    import Hasher

class OfficeWorker(Worker):
    def identify_sample(self, oid):
        indicators = oid.check()
        for i in indicators:
            if i.value == True:
                return {'id':i.id, 'id_name':i.name,'id_description':i.description}
    
    def doc_has_macros(self, vba):
        if vba.detect_vba_macros():
            return True
        else:
            return False
    
    def macro_extraction(self, vba):
        for (filename, stream_path, vba_filename, vba_code) in vba.extract_macros():
            macro_info = {
            'ole_stream'     : stream_path,
            'vba_filename'   : vba_filename,
            'vba_code'       : vba_code
            }
    
        return macro_info
    
    def process(self, sample):
        try:
            hashbot      = Hasher(sample['filename'])
            mymagic      = magic.Magic(mime=True)
            sample_info  = self.identify_sample(oletools.oleid.OleID(sample['filename']))
            vba          = VBA_Parser(sample['filename'])
    
            # Extend the results of sample_info with extra data and add to Splunk
            sample_info['submit_date']   = int(time())
            sample_info['filetype']      = mymagic.from_file(sample['filename'])
            sample_info['sample_type']   = 'office'
            sample_info['id_tag']        = sample['tag']
            sample_info['sha1']          = hashbot.get_sha1()
            sample_info['md5']           = hashbot.get_md5()
            indicators                   = dict()

            if self.doc_has_macros(vba):
                macro = self.macro_extraction(vba)
                data  = VBA_Scanner(macro['vba_code']).scan(include_decoded_strings=False)
    
                i = 1
                for kw_type, keyword, description in data:
                    indicators[str(i)] = {'type':kw_type, 
                                          'keyword':keyword, 
                                          'description':description
                                         } 
                    i+=1

            sample_info['indicators'] = indicators
            self.share_data(sample_info)
            self.store_sample(sample['filename'])
        except Exception, e:
            self.log('{0} - {1} - {2} '.format('docworker',sample,e))
        finally:
            return
