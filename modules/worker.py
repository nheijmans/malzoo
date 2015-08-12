#!/usr/bin/python
"""
This is the worker that will be executed per sample. It collects the information
of the sample via the other modules and then stores these in the Mongo DB.
"""

# Imports 
import time
from modules.yarascan import yarascan
from modules.hashes import Hasher
from modules.strings import strings
from modules.general_info import GeneralInformation
from modules.pe import PeInfo
from modules.database import MongoDatabase
from modules.sample_storager import add_to_repository

def do_work(q, processid):
    """ This function will process the files """
    while True: 
        if q.empty():
            time.sleep(1)
        else:
            sample_path = q.get()
            try:
                start_time = time.time()
                sample, tag = sample_path.split(':')
                print "%s working on %s" % (processid, sample)

                # Create objects from the classes
                hasher = Hasher(sample)
                general_info = GeneralInformation(sample)
                pe_info = PeInfo(sample, 'userdb.txt')
                db_commands = MongoDatabase() 

                ft = general_info.get_filetype()
                db_hash = db_commands.find_hash(hasher.get_md5())['md5']

                if pe_info.packer_detect() != None or pe_info.packer_detect != [] or pe_info.packer_detect != "N.A.":
                    strings_sample = strings(sample)
                else:
                    strings_sample = "Packer detected"

                if  ft[0:4] == 'PE32':
                    # Creating a dictionary with sample information
                    sample_info = { 
                    'filename' : general_info.get_filename(),
                    'filetype' : general_info.get_filetype(),
                    'filesize' : str(general_info.get_filesize()),
                    'md5' : hasher.get_md5(),
                    'sha' : hasher.get_sha1(),
                    'pehash' : hasher.get_pehash(),
                    'imphash' : hasher.get_imphash(),
                    'fuzzy' : hasher.get_fuzzy(),
                    'yara_results' : yarascan(sample),
                    'pe_compiletime' : pe_info.get_compiletime(),
                    'pe_dll' : pe_info.get_dll(),
                    'pe_packer' : pe_info.packer_detect(),
                    'pe_language' : pe_info.get_language(),
                    'original_filename' : pe_info.get_org_filename(),
                    'strings_results' : strings_sample,
                    'tag' : tag
                    }

                    db_commands.add_sample(sample_info)
                    stored = add_to_repository(sample)
                    if stored:
                        print "Sample stored and moved:\t",
                    else:
                        print "Sample stored not moved:\t",
                    print general_info.get_filename()


                else:
                    if ft[0:4] != 'PE32':
                        print "Not a PE:\t",
                        print general_info.get_filename()

                    else:
                        print "Already in DB:\t",
                        print general_info.get_filename()

            except Exception, e:
                print "Error on sample: " + sample_path
                print e
