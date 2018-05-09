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
from configopt import *
from dialogOptions import *
from pageLists import *
from imgProcess import *
from globalprj import *
from taskViewer import *

class AppWindow(QtWidgets.QMainWindow):
    """
    Class for the main menu
    """
    def __init__(self):
        super(AppWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("OpenREC")
        self.setWindowIcon(QtGui.QIcon('icons/icon.png'))

        newProjectAction = QtWidgets.QAction("&New project", self)
        newProjectAction.setShortcut("Ctrl+N")
        newProjectAction.setStatusTip('Create a new project...')
        newProjectAction.triggered.connect(self.new_project)

        openProjectAction = QtWidgets.QAction("&Open project", self)
        openProjectAction.setShortcut("Ctrl+O")
        openProjectAction.setStatusTip('Load an existing project...')
        openProjectAction.triggered.connect(self.open_project)

        optionsAction = QtWidgets.QAction("&Preferences...", self)
        optionsAction.setShortcut("Ctrl+P")
        optionsAction.setStatusTip('Preferences...')
        optionsAction.triggered.connect(self.options)

        exitAction = QtWidgets.QAction("&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip('Quit this application')
        exitAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(newProjectAction)
        fileMenu.addAction(openProjectAction)
        fileMenu.addAction(optionsAction)
        fileMenu.addAction(exitAction)

        tasksMenu = mainMenu.addMenu('&Tasks')
        taskManagerMenu = QtWidgets.QAction("&Manage tasks...", self)
        taskManagerMenu.setShortcut("Ctrl+T")
        taskManagerMenu.setStatusTip('Manager tasks of the system...')
        taskManagerMenu.triggered.connect(self.taskmanager)
        tasksMenu.addAction(taskManagerMenu)
        
        helpMenu = mainMenu.addMenu('&Help')
        helpManagerMenu = QtWidgets.QAction("&About", self)
        helpManagerMenu.setStatusTip('Information about OpenREC...')
        helpManagerMenu.triggered.connect(self.show_about)
        helpMenu.addAction(helpManagerMenu)

        self.ui()


    def ui(self):
        window = QtWidgets.QWidget();
        self.pagesWidget = QtWidgets.QStackedWidget()

        # pages of stages (TODO)
        self.surfacePage = pageLists(title="Mesh Reconstruction", stage="surface")
        self.dcloudPage = pageLists(title="Dense Cloud Stage", stage="dense_cloud",
                                    nextPageList=self.surfacePage)
        self.sfmPage = pageLists(title="SFM Stage", stage="sfm",
                                 nextPageList=self.dcloudPage)
        self.imagesPage = pageLists(title="Image Features Stage", stage="features",
                                    eventManager=imgProcess(),
                                    nextPageList=self.sfmPage)

        self.pagesWidget.addWidget(self.imagesPage)
        self.pagesWidget.addWidget(self.sfmPage)
        self.pagesWidget.addWidget(self.dcloudPage)
        self.pagesWidget.addWidget(self.surfacePage)

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

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)
        window.setLayout(horizontalLayout)
        self.setCentralWidget(window)

        self.pagesWidget.setEnabled(False)
        self.contentsWidget.setEnabled(False)

        self.show()

    def close_application(self):
        try:
            TASK_MANAGER.save()
        except:
            print("Warning: tasks couldn't be saved in line 136 of mainApp.py.")
        fname = CACHE["current_prj"]
        try:
            PROJECT.save(fname)
        except:
            print("Warning: PROJECT cannot saved before exit!")
        # kill all local process
        killProcess()
        sys.exit()

    def new_project (self):
        global PROJECT,CACHE,TASK_MANAGER
        home = os.path.expanduser("~")
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",
                                                         home,
                                                         QtWidgets.QFileDialog.ShowDirsOnly
                                                         | QtWidgets.QFileDialog.DontResolveSymlinks);
        if dir == "":
            return

        fname = os.path.join(dir, "project.prj")
        try:
            TASK_MANAGER.save()
        except:
            print("Warning: tasks cannot be saved.")
        if PROJECT.save(fname) == False:
            QtWidgets.QMessageBox().warning(self, "Problem creating project file",
                                            "The project cannot be created at that directory.")
        else:
            CACHE["current_prj"] = fname
            init_prj()
            self.pagesWidget.setEnabled(True)
            self.contentsWidget.setEnabled(True)
            self.setWindowTitle("OpenS: " + os.path.dirname(CACHE["current_prj"]))

    def open_project (self):
        global PROJECT, CACHE, TASK_MANAGER
        try:
            TASK_MANAGER.save()
        except:
            print("Warning: tasks cannot be saved.")
        home = os.path.expanduser("~")
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      "Open Image",
                                                      home, "Project Files (*.prj);; All files (*.*)")
        loaded = False
        try:
            if fname[0] == "":
                return

            if PROJECT.open(fname[0]) == False:
                QtWidgets.QMessageBox().warning(self, "Problem loading project file",
                                                "The project cannot be loaded for that file.")
            else:
                TASK_MANAGER.load()
                CACHE["current_prj"] = fname[0]
                self.pagesWidget.setEnabled(True)
                self.contentsWidget.setEnabled(True)
                self.setWindowTitle("OpenS: " + os.path.dirname(CACHE["current_prj"]))
                loaded = True
        except:
                QtWidgets.QMessageBox().warning(self, "Problem loading project file",
                                                "Error parsing the file: project file seems corrupt.")
        if loaded:
            # update the lists in the pages
            self.imagesPage.loadData()
            # TODO: rest of the lists

    def warningLostProject(self):
        """ A simple warning message """
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Changes may be LOST if you press OK.")
        msg.setInformativeText("This project was not saved, are you sure you want to start another project without saving this project first?")
        msg.setWindowTitle("Project was not saved")
        msg.setDetailedText("If you press OK now, the current project will not be saved. Instead, a new project will be created and changes not saved in disk will be lost forever.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        ret = msg.exec_()
        if ret != QtWidgets.QMessageBox.Ok:
            return True
        else:
            return False

        
    def options (self):
        c = dialogOptions(self)
        c.exec_()
        return


    def addIcons(self):
        configButton1 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton1.setIcon(QtGui.QIcon("icons/images.png"));
        configButton1.setText("Pictures");

        configButton2 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton2.setIcon(QtGui.QIcon("icons/sfm_cameras.png"));
        configButton2.setText("3D Cameras");

        configButton3 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton3.setIcon(QtGui.QIcon("icons/final_cloud.png"));
        configButton3.setText("Final Clouds");

        configButton4 = QtWidgets.QListWidgetItem(self.contentsWidget)
        configButton4.setIcon(QtGui.QIcon("icons/final_mesh.png"));
        configButton4.setText("Final Meshes");

        return

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))
        self.pagesWidget.currentWidget().loadData() 

    def taskmanager (self):
        c = taskManager(self)
        c.exec_()
        return

    def show_about (self):
        license = """
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
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText("OpenREC - version 0.1")
        msg.setInformativeText("OpenREC is under GPLv3 license. \nPress 'Show Details...' below to see all the information about this license.")
        msg.setWindowTitle("OpenREC version 0.1 \n author: Germán Arroyo (arroyo@ugr.es) \n Universidad de Granada \n Spain")
        msg.setDetailedText(license)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
   
        return
