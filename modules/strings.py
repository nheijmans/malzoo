#!/usr/bin/python
"""
A function that extracts all strings from a portable executable of 
four characters or longer based on the regex supplied. 

This script can be executed on itself by supplying a single file. 
Usage: python strings.py putty.exe

"""

# imports
import re
import sys

def strings(filename):
    """ Function that returns all strings in a file with a minimum length of 4 """

    with open(filename, 'rb') as f:
        data    = f.read() # Read all data in memory
        regexp  = '[A-Za-z0-9/\-:.,_$%()[\]<> ]{4,}'
        strings = re.findall(regexp, data)
        
        strings_UTF = [unicode(s,'utf-8','ignore') for s in strings]
        return strings_UTF


# If the script is running on itself, one argument is accepted and will print the strings for that file.
if __name__ == '__main__':
    if len(sys.argv) == 2:
        result = strings(sys.argv[1])
        for entry in result:
            print entry

    elif len(sys.argv) > 2:
        print "Too many arguments, I can only handle one file at a time"

    else:
        print "No file to process... Quitting now!"
