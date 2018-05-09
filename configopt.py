# -*- coding: utf-8 -*-

"""
        OpenREC is an extendable framework for reconstruction of 3D models from
        photographs.
  
        Copyright (C) 2018  Germán Arroyo.

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.

        You can contact the author via email to <arroyo@ugr.es>,
        or in a more traditional way sending a letter to
        
        Germán Arroyo Moreno
        Departamento de Lenguajes y Sistemas Informáticos
        ETS Ingenierías Informática y de Telecomunicación,
        C/Periodista Daniel Saucedo Aranda, s/n · E-18071 GRANADA (Spain)
        Universidad de Granada.
"""

import os
import json

class ConfigOpt:
    """
    Class for the complete project
    """

    def __init__(self):
        """ Constructor """
        self.var = {}
        return

    def save(self, fname):
        """ Save the current project """

        #if (self.var["local_path"] is None):
        #    return False # project doesn't exist

        #fname = os.path.join(self.var["local_path"], 'project.prj')
        if fname is None:
            return False
        file = open(fname, 'w')
        if file is None:
            return False # File cannot be created

        file.write(json.dumps(self.var, sort_keys=True, indent=4))
        file.close()
        return True


    def open(self, fname):
        """ Load a project from a given file"""
        if fname is None:
            return False
        file = open(fname, 'r')
        if file is None:
            return False # File cannot be opened
        tmpcfg = self.var
        self.var = json.loads(file.read())
        file.close()
        if self.var == None:
            self.var = tmpcfg
            return False
        return True

    def search(self, var, default=None):
        v = self.var
        # if variable not found, return default
        if v is None:
            return default
        # split the path
        path = var.split("/")
        #print("SEARCHING: " + str(path))
        for p in path:
            #print("  -> " + p)
            try:
                v = v[p]
                #print("Now v is " + str(v))
            except: # not found
                #print("Not found v[p]: " + str(p) + " in " + str(v))
                return default
        return v

    def __getitem__(self, key):
        return self.search(key)

    def __setitem__(self, key, value):
        v = self.var
        # if variable not found, return default
        if v is None:
            return default
        # split the path
        path = key.split("/")
        #print("SEARCHING: " + str(path))
        finalkey = path[-1]
        for p in path[:-1]:
            #print("  -> " + p)
            try:
                v = v[p]
                #print("Now v is " + str(v))
            except: # not found
                #print("Not found v[p]: " + str(p) + " in " + str(v))
                return None
        v[finalkey] = value


    @staticmethod
    def merge(x, y):
         """ Given two dicts, merge them into a new dict as a shallow copy. """
         z = x.copy()
         z.update(y)
         return z
