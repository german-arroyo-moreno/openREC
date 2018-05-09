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

import sys
from PyQt5 import QtGui, QtCore, QtWidgets, Qt
from pageServerCfg import *
from pageLocalCfg import *
from pageProjectCfg import *

class dialogOptions(QtWidgets.QDialog):
    """
    Class for the options dialog
    """
    def __init__(self, parent=None):
        super(dialogOptions, self).__init__(parent)
        #self.setGeometry(200, 200, 800, 400)
        self.setWindowTitle("Config Dialog...")
        self.ui()

    def ui(self):
        self.pagesWidget = QtWidgets.QStackedWidget()
        self.pagesWidget.addWidget(pageLocalCfg())
        self.pagesWidget.addWidget(pageServerCfg())
        self.pagesWidget.addWidget(pageProjectCfg())

        self.contentsWidget = QtWidgets.QListWidget()
        self.contentsWidget.setViewMode(QtWidgets.QListView.IconMode)
        self.contentsWidget.setIconSize(QtCore.QSize(96, 84))
        self.contentsWidget.setMovement(QtWidgets.QListView.Static)
        self.contentsWidget.setMaximumWidth(130)
        self.contentsWidget.setMinimumHeight(300)
        self.contentsWidget.setSpacing(12)

        self.addIcons()

        self.contentsWidget.setCurrentRow(0)
        self.contentsWidget.currentItemChanged.connect(self.changePage)

        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close_application)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        horizontal2Layout = QtWidgets.QHBoxLayout()
        horizontal2Layout.addWidget(closeButton)
        horizontal2Layout.addStretch(1)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        #mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(horizontal2Layout)
        self.setLayout(mainLayout)

    def addIcons(self):
        configButton1 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton1.setIcon(QtGui.QIcon("icons/local_configuration.png"));
        configButton1.setText("Local Options");

        configButton2 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton2.setIcon(QtGui.QIcon("icons/global_configuration.png"));
        configButton2.setText("Server Options");

        configButton2 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton2.setIcon(QtGui.QIcon("icons/project_configuration.png"));
        configButton2.setText("Project");

        return

    def close_application(self):
        self.close()
        return

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

