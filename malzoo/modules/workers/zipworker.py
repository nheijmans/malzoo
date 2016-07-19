#!/usr/bin/python
"""
Module to extract (encrypted) ZIP files, optionally with a supplied
password. 
"""
#Parent
from malzoo.common.abstract import Worker

#Default imports
from time import time
import zipfile

#Malzoo imports
from malzoo.modules.tools.saveobject import SaveObject
from malzoo.modules.tools.hashes       import Hasher
from malzoo.modules.tools.general_info import GeneralInformation

class ZipWorker(Worker):
    def process(self, sample, tag, pwd=None):
        try:
            if zipfile.is_zipfile(sample):
                zf = zipfile.ZipFile(sample, 'r')
            else:
                return

            hasher  = Hasher(sample)
            general_info = GeneralInformation(sample)
            saveobj = SaveObject()
            zfiles = zf.namelist()
            zippedfiles = []
            for fn in zfiles:
                data = zf.read(fn,pwd)
                result = saveobj.save(data, fn, tag, self.dist_q)

            sample_info = dict()
            sample_info['sample_type'] = 'zip'
            sample_info['files']       = ','.join(zfiles)
            sample_info['filename']    = sample.split('/')[-1]
            sample_info['id_tag']      = tag
            sample_info['md5']         = hasher.get_md5()
            sample_info['sha1']        = hasher.get_sha1()
            sample_info['filesize']    = general_info.get_filesize()
            sample_info['filetype']    = general_info.get_filetype()
            sample_info['submit_date'] = int(time())

            self.share_data(sample_info)
            self.store_sample(sample)
        except Exception as e:
            print "ZipWorker: Error on sample", e
        finally:
            return

