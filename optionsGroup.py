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

class optionsGroup(QtWidgets.QGroupBox):
    """Global configuration page"""

    def __init__(self, title="", options=[], event=None, parent=None):
        """
        Create a titled group with a list of options, if some value change the
        callback named "event" is called: event(dict_of_variables).

        options = [variable, default value]
        options = [variable, default value, [list_of_options]]
        options = [variable, bool value, "BOOL"]
        options = [variable, number value, min (optional), max (optional), step (optional)]
        """ 
        super(optionsGroup, self).__init__(parent)
        self.setTitle(title)

        self.var = {}
        self.evt = event
        self.combobox = {}
        self.textinput = {}
        self.checkbox = {}
        self.number = {}

        mainLayout = QtWidgets.QVBoxLayout()
        for e in options:
            #print(e[0] + " = " + str(e[1]))
            hLayout = QtWidgets.QHBoxLayout()
            l = QtWidgets.QLabel(str(e[0]) + ": ")
            hLayout.addWidget(l)
            if len(e) >= 3 and isinstance(e[2], str) and e[2].lower() ==  "bool": # checkbox
                #print(" is bool")
                c = QtWidgets.QCheckBox()
                self.checkbox[e[0]] = c
                if e[1]:
                    c.setCheckState(Qt.Qt.Checked)
                else:
                    c.setCheckState(Qt.Qt.Unchecked)
                c.stateChanged.connect(self.updated)
            elif isinstance(e[1], float) or isinstance(e[1], int): # number
                #print(" is number")
                c = QtWidgets.QDoubleSpinBox()
                if len(e) >= 3:
                    c.setMinimum(e[2])
                if len(e) >= 4:
                    c.setMaximum(e[3])
                if len(e) >= 5:
                    c.setSingleStep(e[4])
                c.setValue(e[1])
                self.number[e[0]] = c
                c.valueChanged.connect(self.updated)
            elif len(e) >= 3 and isinstance(e[2], list): # combobox
                #print(" is combobox")
                c = QtWidgets.QComboBox()
                c.insertItems(0, e[2])
                c.setEditable(False)
                try:
                    c.setCurrentIndex(e[2].index(e[1]))
                except:
                    c.setCurrentIndex(0)
                self.combobox[e[0]] = c
                c.currentIndexChanged.connect(self.updated)
            else: # text field
                #print(" is text")
                c = QtWidgets.QLineEdit(str(e[1]))
                self.textinput[e[0]] = c
                c.textChanged.connect(self.updated)
            # add all components to the main layout
            hLayout.addWidget(c)
            mainLayout.addLayout(hLayout)
        # set the main layout
        self.setLayout(mainLayout)
        return

    def updated(self, var):
        for c in self.combobox:
            cmb = self.combobox[c]
            self.var[c] = cmb.itemText(cmb.currentIndex())
        for c in self.textinput:
            self.var[c] = self.textinput[c].text()
        for c in self.number:
            self.var[c] = self.number[c].value()
        for c in self.checkbox:
            self.var[c] = (self.checkbox[c].checkState() == Qt.Qt.Checked)
        if not (self.evt is None):
            self.evt(self.var)
