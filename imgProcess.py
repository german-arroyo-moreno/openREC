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
import shutil
from globalprj import *

class imgProcess:

    def __init__(self):
        return

    def on_list_change(self, sender):
        global PROJECT, CACHE
        dirc = os.path.dirname(CACHE["current_prj"])
        dirc = os.path.join(dirc, PROJECT["paths"]["features"])
        for name in PROJECT["data"]:
            folder = os.path.join(dirc, name)
            if not os.path.isdir(folder):
                os.makedirs(folder)

        PROJECT.save(CACHE["current_prj"])
        return True

    def on_images_change(self, sender, selected, files):
        global PROJECT, CACHE
        self.on_list_change(sender)
        dirc = os.path.dirname(CACHE["current_prj"])
        dirc = os.path.join(dirc, "images")
        folder = os.path.join(dirc, selected)

        for f in files:
            shutil.copy(f, folder)

        return True

    def on_remove_image(self, selected, filef):
        global CACHE
        dirc = os.path.dirname(CACHE["current_prj"])
        dirc = os.path.join(dirc, "images")
        folder = os.path.join(dirc, selected)
        filef = os.path.join(folder, filef)
        os.remove(filef)
        return

    def on_process(self, sender):
        return

    def on_remote_process(self, sender):
        return
