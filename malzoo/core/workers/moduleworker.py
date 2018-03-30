#!/usr/bin/python
"""
The module worker will execute all custom modules in the modules/ directory
with the package delivered by malzoo core. This contains the MD5, filepath
and filename and the tag assigned.
"""

#Parent
from malzoo.common.abstract import Worker
from malzoo.common.abstract import CustomModule

import pkgutil
import inspect
import importlib

import malzoo.modules as modules

class ModuleWorker(Worker):
    def load_modules(self):
        try:
            plugins = dict()
            for loader, module_name, ispkg in pkgutil.walk_packages(modules.__path__, modules.__name__+'.'):
                if ispkg:
                    continue
                module = importlib.import_module(module_name)

                for member_name, member_object in inspect.getmembers(module):
                    if inspect.isclass(member_object):
                        if issubclass(member_object, CustomModule) and member_object is not CustomModule:
                            plugins[member_object.name] = dict(obj=member_object,
                                                               enabled=member_object.enabled,
                                                               name=member_object.name
                                                               )
        except Exception as e:
            self.log('module worker - load_modules - '+str(e))
            plugins = None
        finally:
            return plugins

    def process(self, sample):
        try:
            plugins = self.load_modules()
            threads = list()
            if plugins:
                for plugin in plugins.keys():
                    # FILENAME AND TAG ARE GIVEN IN THE ABSTRACT. ADD THAT HERE CORRECTLY. THINK OF ADDING MD5 AS WELL
                    # check if the plugin is enabled and if so, start it
                    if plugins[plugin]['obj'].enabled:
                        t = plugins[plugin]['obj'](sample)
                        t.start()
                        threads.append(t)

                for t in threads:
                    t.join()
            else:
                self.log('module worker - process  - no plugins')

        except Exception as e:
            self.log('module worker - process  - '+str(e))
        finally:
            return

