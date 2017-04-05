#!/usr/bin/python
"""
File is part of Malzoo

The class GeneralInformation is used to extract the following information:
    [*] Filename
    [*] Filetype
    [*] Filesize

This is very simple at the moment but can be expanded with other functions
that are considered "general information". 

"""
# Imports
import os
import sys
import magic

class GeneralInformation:
    """ Class for getting filename, filetype and filesize of a sample """
    def __init__(self, filename):
        self.filename = filename

    def get_filename(self):
        """ Function that returns the self.filename, splitted from the path """
        splitted = self.filename.split('/')
        fn       = splitted[len(splitted)-1]
        return fn

    def get_filetype(self):
        """ Function that returns the filetype of the sample """
        ft = magic.from_buffer(open(self.filename).read(2048), mime=True)
        return ft

    def get_filesize(self):
        """ Function that returns the calculated filesize """
        # TODO Calclate the size in KB
        fs = os.path.getsize(self.filename)
        return fs
