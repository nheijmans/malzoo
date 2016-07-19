#!/usr/bin/python
"""
File is part of Malzoo

The Hasher class is build to generate a number of hashes of a sample. 
Currently, it can calculate:
    [*] MD5
    [*] SHA-1
    [*] PE hash
    [*] Fuzzy hash
    [*] Import hash

Note that only PE files are supported with PE hash

TODO:
    [ ] Peform a filetype check
    [ ] Add more hash types
    [ ] Create exception handling
"""

# Imports
import sys
import pefile
from hashlib import md5 as md5sum
from hashlib import sha1 as sha1sum
from pydeep import hash_file as fuzzy
from pehash import pehash as ph

class Hasher:
    """ Class for calculating MD5, SHA-1, fuzzy and PE hashes """
    def __init__(self, filename):
        self.filename = filename

    def get_md5(self):
        """ Generate MD5 of the sample """
        with open(self.filename, 'rb') as f:
                md5_hash = md5sum(f.read()).hexdigest()

        return md5_hash

    def get_sha1(self):
        """  Generate SHA-1 of the sample """
        with open(self.filename, 'rb') as f:
                sha1_hash = sha1sum(f.read()).hexdigest()

        return sha1_hash

    def get_fuzzy(self):
        """ Generate Fuzzy of the sample """
        fuzzy_hash = fuzzy(self.filename)
        return fuzzy_hash

    def get_pehash(self):
        """ Generate PE hash of the sample """
        pe_hash = ph(self.filename)
        return pe_hash

    def get_imphash(self):
        imphash = ''
        try:
            pe = pefile.PE(self.filename)
            imphash = pe.get_imphash()

        except:
            #Do something with logging
            pass

        finally:
            return imphash
