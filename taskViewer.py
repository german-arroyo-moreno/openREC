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
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout,QDialog,QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot,QTimer
from globalprj import *

class taskManager(QDialog):
 
    def __init__(self, parent=None):
        super(taskManager,self).__init__(parent)
        self.title = 'Task manager'
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.populate)
        self.timer.start(500)
 
    def initUI(self):
        self.setWindowTitle(self.title)
 
        self.createTable()
 
        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 
 
        # Show widget
        self.show()
 
    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(0)
        header = ("Time signature", "Task", "Status", "Blocked by", "Description", "Local/Remote")
        self.tableWidget.setColumnCount(len(header))
        self.tableWidget.setHorizontalHeaderLabels(header)
        self.populate()
        # table selection change
        self.tableWidget.move(0,0)
        self.tableWidget.setSortingEnabled(True)
        #self.tableWidget.doubleClicked.connect(self.on_click)
         
    def populate(self):
        """ Populate the list of tasks"""
        global TASK_MANAGER
        
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(TASK_MANAGER.tasks()))

        index = 0
        for task in TASK_MANAGER.tasks():
            self.tableWidget.setItem(index, 0, QTableWidgetItem(task.date))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(task.task.name))
            if task.task.state != "done" and task.task.state != "aborted":
                statButton = QPushButton(task.task.state)
                statButton.setStyleSheet("background-color: red")
                model = self.tableWidget.model()
                self.tableWidget.setIndexWidget(model.index(index,2), statButton);
                statButton.clicked.connect(lambda x,y=task: self.on_cancel_task(y.task))

                # if task is waiting say why
                if task.task.state == "waiting":
                    if task.data[0] == "task":
                        text = "on task: " + task.data[1].name
                    else:
                        text = "on files: " + str(task.data[1])
                    self.tableWidget.setItem(index, 3, QTableWidgetItem(text))

            else:
                self.tableWidget.setItem(index, 2, QTableWidgetItem(task.task.state))
            self.tableWidget.setItem(index, 4, QTableWidgetItem(task.task.description))
            if task.task.local:
                text = "local"
            else:
                text = "remote"
            self.tableWidget.setItem(index, 5, QTableWidgetItem(text))
            index = index + 1

        self.tableWidget.setSortingEnabled(True)

 
    #@pyqtSlot()
    #def on_click(self):
    #    print("\n")
    #    for currentQTableWidgetItem in self.tableWidget.selectedItems():
    #        print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
 

    @pyqtSlot()
    def on_cancel_task(self, task):
        global TASK_MANAGER
        #print("Cancel task[" + str(task.name) +  "]")
        task.cancel()
        return
