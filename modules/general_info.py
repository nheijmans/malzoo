#!/usr/bin/python
"""
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
        ft = magic.from_buffer(open(self.filename).read(1024))
        return ft

    def get_filesize(self):
        """ Function that returns the calculated filesize """
        # TODO Calclate the size in KB
        fs = os.path.getsize(self.filename)
        return fs


    
    
# If the script is running on itself, one argument is accepted and will print the strings for that file.
if __name__ == '__main__':
    if len(sys.argv) == 2:
        general_info = GeneralInformation(sys.argv[1])
        filename     = general_info.get_filename()
        filetype     = general_info.get_filetype()
        filesize     = general_info.get_filesize()

    elif len(sys.argv) > 2:
        print "Too many arguments, I can only handle one file at a time"

    else:
        print "No file to process... Quitting now!"
