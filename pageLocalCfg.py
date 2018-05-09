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
from PyQt5 import QtGui, QtCore, QtWidgets, Qt
from optionsGroup import *
from globalprj import *

class pageLocalCfg(QtWidgets.QWidget):
    """
    Local configuration page in preferences.
    CONFIG global variable is required by this class.
    """

    def __init__(self):
        global CONFIG
        super(pageLocalCfg, self).__init__()
        configGroup = QtWidgets.QLabel("<h2>Local configuration:</h2>")

        # syncronized with globalprj.py
        openMVGOptions = optionsGroup("OpenMVG options:",
                                      [
                                          ["Binaries path", CONFIG["openMVG/Binaries path"]],
                                          ["Database path", CONFIG["openMVG/Database path"]],

                                      ],
                                      self.updateOptions1)
       # syncronized with globalprj.py
        CMVSOptions = optionsGroup("CMVS/PMVS2 options:",
                                   [
                                       ["Binaries path", CONFIG["CMVS/Binaries path"]]
                                       
                                   ],
                                   self.updateOptions2)
       # syncronized with globalprj.py
        PoissonOptions = optionsGroup("PoissonRecon options:",
                                      [
                                          ["Binaries path", CONFIG["Poisson/Binaries path"]]
                                          
                                      ],
                                      self.updateOptions3)
       # syncronized with globalprj.py
        MeshlabOptions = optionsGroup("Meshlab options:",
                                      [
                                          ["Binaries path", CONFIG["Meshlab/Binaries path"]]                                 
                                      ],
                                      self.updateOptions4)
        # syncronized with globalprj.py
        SSHOptions = optionsGroup("SSH/SCP options:",
                                  [
                                     ["Binaries path", CONFIG["SSH/Binaries path"]]
                                  ],
                                  self.updateOptions5)
        #layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(openMVGOptions)
        #layout.addWidget(CMVSOptions)
        #layout.addWidget(PoissonOptions)
        #layout.addWidget(MeshlabOptions)
        #configGroup.setLayout(layout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(configGroup)
        mainLayout.addWidget(openMVGOptions)
        mainLayout.addWidget(CMVSOptions)
        mainLayout.addWidget(PoissonOptions)
        mainLayout.addWidget(MeshlabOptions)
        mainLayout.addWidget(SSHOptions)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        return

    def updateOptions1(self, var):
        global CONFIG
        CONFIG["openMVG"] = ConfigOpt.merge(CONFIG["openMVG"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)

    def updateOptions2(self, var):
        global CONFIG
        CONFIG["CMVS"] = ConfigOpt.merge(CONFIG["CMVS"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)

    def updateOptions3(self, var):
        global CONFIG
        CONFIG["Poisson"] = ConfigOpt.merge(CONFIG["Poisson"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)

    def updateOptions4(self, var):
        global CONFIG
        CONFIG["Meshlab"] = ConfigOpt.merge(CONFIG["Meshlab"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)

    def updateOptions5(self, var):
        global CONFIG
        CONFIG["SSH"] = ConfigOpt.merge(CONFIG["SSH"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)
