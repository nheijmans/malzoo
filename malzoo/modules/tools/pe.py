#!/usr/bin/python
"""
The PeInfo class is build to extract information from a Portable Executable
like:
    [*] Extract DLL files if possible
    [*] Extact CPU architecture
    [*] Extract compilation time
    [*] Detect if a packer is used
    [*] Extract compilation language

Only PE files are supported by this module. It can be executed on itself with
one argument provided which is the PE file.

Usage example: python pe.py putty.exe
This will print the data listed above. 

"""
# Imports
import sys
import magic
import pefile
import peutils
import datetime
import collections

class PeInfo:
    def __init__(self, filename, userdb):
        try:
            self.userdb     = userdb
            self.pe         = pefile.PE(filename)
            self.language   = []
            self.filename   = filename

        except pefile.PEFormatError:
            self.pe = False
            pass

    def get_dll(self):
        """ Extract the imported DLL files from the PE file """
        # If the PE has the attribute, create a list with DLL's
        if self.pe != False and hasattr(self.pe, 'DIRECTORY_ENTRY_IMPORT'):
            dll_list = [i.dll for i in self.pe.DIRECTORY_ENTRY_IMPORT]
            return ','.join(dll_list)
        else:
            return None
    
    def get_cpu_type(self):
        """ Return the CPU architecture (x86, x64) """
        if self.pe != False:
            machine = 0  
            machine = self.pe.FILE_HEADER.Machine  

            return pefile.MACHINE_TYPE[machine] 

        else:
            return None

    def get_compiletime(self):
        """ Extract the compile time """
        if self.pe != False:
            compiletime = datetime.datetime.fromtimestamp(self.pe.FILE_HEADER.TimeDateStamp)  
            return compiletime.strftime("%Y-%m-%d %H:%M:%S")

        else:
            return None

    def packer_detect(self):  
        """ attempt to detect the packer used """
        if self.pe != False:
            signatures  = peutils.SignatureDatabase(self.userdb)
            matches     = signatures.match_all(self.pe, ep_only=True)  
            result      = ''
            
            if matches != None:
                for match in matches:
                    m       = ','.join(match)
                    result  = result+m

                return result
            else:
                return None
        else:
            return None

    def check_rsrc(self):
        """ Function needed to determine the compilation language """
        try:
            ret = {}
            if hasattr(self.pe, 'DIRECTORY_ENTRY_RESOURCE'):
                i = 0
                for resource_type in self.pe.DIRECTORY_ENTRY_RESOURCE.entries:
                    if resource_type.name is not None:
                        name = "%s" % resource_type.name
                    else:
                        name = "%s" % pefile.RESOURCE_TYPE.get(resource_type.struct.Id)
                    if name == None:
                        name = "%d" % resource_type.struct.Id
                    if hasattr(resource_type, 'directory'):
                        for resource_id in resource_type.directory.entries:
                            if hasattr(resource_id, 'directory'):
                                for resource_lang in resource_id.directory.entries:
                                    try:
                                        data = self.pe.get_data(resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size)
                                        filetype = magic.from_buffer(open(self.filename).read(1024)) 
                                        lang = pefile.LANG.get(resource_lang.data.lang, 'qq_*unknown*')
                                        sublang = pefile.get_sublang_name_for_lang( resource_lang.data.lang, resource_lang.data.sublang )
                                        ret[i] = (name, resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size, filetype, lang, sublang)
                                        i += 1
                                    except pefile.PEFormatError:
                                        pass
        except:
            ret = False 
            pass
        finally:
            return ret

    def get_language(self):
        """ 
        Returns the compilation language and processes the returned
        data of check_rsrc
        """
        if self.pe != False and self.check_rsrc() != False:
            resources = self.check_rsrc()
            ret = []
            lang_holder = []
            for rsrc in resources.keys():
                (name,rva,size,type,lang,sublang) = resources[rsrc]
                lang_holder.append(lang)
                lang_count  = collections.Counter(lang_holder)
                lang_common = lang_count.most_common(1)
                for lang_likely,occur in lang_common:
                    ret = lang_likely.split('_')[1]
                if len(ret) > 0:
                    return ret
                else:
                    return None
        else:
            return None

    def get_org_filename(self):
        if self.pe != False and self.check_rsrc() != False:
            try:
                self.pe.full_load()
                fn = self.pe.FileInfo[0].StringTable[0].entries['OriginalFilename']
            except:
                fn = None
                pass
            finally:
                return fn
        else:
            return None
