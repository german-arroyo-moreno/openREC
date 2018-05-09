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

class pageServerCfg(QtWidgets.QWidget):
    """
    Local configuration page in preferences.
    CONFIG global variable is required by this class.
    """

    def __init__(self):
        global CONFIG
        super(pageServerCfg, self).__init__()
        configGroup = QtWidgets.QLabel("<h2>Server configuration:</h2>")

        # syncronized with globalprj.py
        serverOptions = optionsGroup("Server options:",
                                     [
                                         ["Address", CONFIG["server/Address"]],
                                         ["User (optional)", CONFIG["server/User (optional)"]],
                                         ["Remote path", CONFIG["server/Remote path"]], 
                                         ["NOHUP server path", CONFIG["server/NOHUP server path"]],
                                         ["Last remote task (Advanced option)", CONFIG["server/Last remote task (Advanced option)"], 1, 9223372036854775806],
                                         ["Path to OpenMVG", CONFIG["server/openMVG/Binaries path"]],
                                         ["Path to OpenMVG database", CONFIG["server/openMVG/Database path"]],
                                         ["Path to CMVS/PVMS2", CONFIG["server/CMVS/Binaries path"]],
                                         ["Path to PoissonRecon", CONFIG["server/Poisson/Binaries path"]]
                                     ],
                                     self.updateOptions1)
        # syncronized with globalprj.py
        SSHOptions = optionsGroup("SSH options:",
                                  [
                                      ["SSH Options", CONFIG["SSH/SSH Options"]],
                                      ["Certificate file (optional)", CONFIG["SSH/Certificate file (optional)"]]
                                  ],
                                  self.updateOptions2)
        #layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(openMVGOptions)
        #layout.addWidget(CMVSOptions)
        #layout.addWidget(PoissonOptions)
        #layout.addWidget(MeshlabOptions)
        #configGroup.setLayout(layout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(configGroup)
        mainLayout.addWidget(serverOptions)
        mainLayout.addWidget(SSHOptions)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)
        return

    def updateOptions1(self, var):
        global CONFIG
        CONFIG["server"] = ConfigOpt.merge(CONFIG["server"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)

    def updateOptions2(self, var):
        global CONFIG
        CONFIG["SSH"] = ConfigOpt.merge(CONFIG["SSH"], var)
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen)
