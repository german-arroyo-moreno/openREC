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
import re
import os

def replacePathInJson(srcfilename, dstfilename, newpath):
    """ Search and replace the path for image files of
    a json data file to a new path """
    with open(srcfilename, 'r') as srcf:
        text = srcf.read()
        srcf.close()
        p = re.compile('"root_path":[ \t]".*",') # reg. expr.
        #text, replacements = p.subn('|||', text)
        text, replacements = p.subn('"root_path": "' + newpath + '",', text)
        dstf = open(dstfilename, 'w')
        dstf.write(text)
        dstf.close()


def requiredFilesForSFM(mypath, path2):
    """ Search all image files and replace their names as required for next stage """
    required_files = []
    for f in os.listdir(mypath):
        if os.path.isfile(os.path.join(mypath, f)):
            # add .feat
            data = os.path.splitext(f)
            if (data[1] == ".jpg" or data[1] == ".JPG" or data[1] == ".png" or
                data[1] == ".PNG" or data[1] == ".tiff" or data[1] == ".TIFF"):
                feat = data[0]+".feat"
                desc = data[0]+".desc"
                required_files.append(os.path.join(path2, feat))
                required_files.append(os.path.join(path2, desc))
    return required_files
