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
import glob, os
from PyQt5 import QtGui, QtCore, QtWidgets, Qt
from globalprj import *
from launcherFeaturesOptions import *
from launcherSFMOptions import *
from launcherDenseOptions import *
from launcherSurfaceOptions import *
from webBrowser import * 
from meshlabFile import *

class pageLists(QtWidgets.QWidget):
    """Global configuration page"""

    def __init__(self, title, stage=None, eventManager=None, nextPageList=None):
        """
        stage can be one of these:
        "features", "sfm", "dense_cloud", "surface"
        """
        super(pageLists, self).__init__()
        configGroup = QtWidgets.QGroupBox(title);

        self.stage = stage
        self.selected = None
        self.evt = eventManager
        self.nextPageList = nextPageList

        # left list
        leftLayout = QtWidgets.QVBoxLayout()
        self.leftList = QtWidgets.QListWidget()
        self.leftList.setMaximumWidth(256)

        hLeftBLayout = QtWidgets.QHBoxLayout()
        addButtonLeft = QtWidgets.QPushButton("")
        addButtonLeft.setIcon(QtGui.QIcon("icons/add.png"))
        addButtonLeft.setIconSize(QtCore.QSize(32,32))
        delButtonLeft = QtWidgets.QPushButton("")
        delButtonLeft.setIcon(QtGui.QIcon("icons/delete.png"))
        delButtonLeft.setIconSize(QtCore.QSize(32,32))
        viewButtonLeft = QtWidgets.QPushButton("")
        viewButtonLeft.setIcon(QtGui.QIcon("icons/view.png"))
        viewButtonLeft.setIconSize(QtCore.QSize(32,32))
        if self.stage == "features":
            hLeftBLayout.addWidget(addButtonLeft)
            hLeftBLayout.addWidget(delButtonLeft)
        else:
            hLeftBLayout.addWidget(viewButtonLeft)
        #hLeftBLayout.addStretch(1)
        leftLayout.addWidget(self.leftList)
        leftLayout.addLayout(hLeftBLayout)
        addButtonLeft.clicked.connect(self.addLeft)
        delButtonLeft.clicked.connect(self.delLeft)
        viewButtonLeft.clicked.connect(self.viewLeft)
        self.leftList.currentItemChanged.connect(self.leftDirChanged)
        mode = self.leftList.selectionMode()
        #mode.dataChanged.connect(self.leftDirRenamed)

        # middle buttons
        self.middleLayout = QtWidgets.QVBoxLayout()
        localCompute = QtWidgets.QPushButton("Local Task...")
        remoteCompute = QtWidgets.QPushButton("Remote Task...")
        localCompute.clicked.connect(self.localTask)
        remoteCompute.clicked.connect(self.remoteTask)
        self.middleLayout.addWidget(localCompute)
        self.middleLayout.addWidget(remoteCompute)
        localCompute.setMaximumWidth(100)

        # right list
        self.rightLayout = QtWidgets.QVBoxLayout()
        self.rightList = QtWidgets.QListWidget()
        hRightBLayout = QtWidgets.QHBoxLayout()
        addButtonRight = QtWidgets.QPushButton("")
        addButtonRight.setIcon(QtGui.QIcon("icons/add.png"))
        addButtonRight.setIconSize(QtCore.QSize(32,32))
        delButtonRight = QtWidgets.QPushButton("")
        delButtonRight.setIcon(QtGui.QIcon("icons/delete.png"))
        delButtonRight.setIconSize(QtCore.QSize(32,32))
        viewButtonRight = QtWidgets.QPushButton("")
        viewButtonRight.setIcon(QtGui.QIcon("icons/view.png"))
        viewButtonRight.setIconSize(QtCore.QSize(32,32))
        if self.stage == "features":
            hRightBLayout.addWidget(addButtonRight)
            hRightBLayout.addWidget(delButtonRight)
        else:
            hRightBLayout.addWidget(viewButtonRight)
            hRightBLayout.addWidget(delButtonRight)
        #hRightBLayout.addStretch(1)
        self.rightLayout.addWidget(self.rightList)
        self.rightLayout.addLayout(hRightBLayout)
        if self.stage == "features":
            self.rightList.setViewMode(QtWidgets.QListView.IconMode)
            self.rightList.setIconSize(QtCore.QSize(256, 256))
            self.rightList.setMovement(QtWidgets.QListView.Static)
            self.rightList.setResizeMode(QtWidgets.QListView.Adjust)
            self.rightList.setMinimumHeight(300)

        self.rightList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        addButtonRight.clicked.connect(self.addRight)
        delButtonRight.clicked.connect(self.delRight)
        viewButtonRight.clicked.connect(self.viewRight)
        
        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addLayout(leftLayout)
        horizontalLayout.addLayout(self.middleLayout)
        horizontalLayout.addLayout(self.rightLayout)

        configGroup.setLayout(horizontalLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(configGroup)

        self.setLayout(mainLayout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.monitorTasks)
        self.timer.start(1000)

        
        return

    def loadData(self):
        global CACHE,PROJECT
        # add to the list the objects inserted in data
        self.leftList.clear()
        self.rightList.clear()
        path = os.path.dirname(CACHE["current_prj"])
        path = os.path.join(path, PROJECT["paths"][self.stage])
        # REVIEW
        #print(self.stage + " " + path)
        if not os.path.isdir(path):
            return
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path,f)):
                alias = PROJECT["alias"][f]
                #print(self.stage + " ; " + f + " : " + alias)
                self.addItem(f, "left", alias)

    def addLeft(self):
        global PROJECT
        name = "Bunch_" + str(PROJECT["next_id"])
        PROJECT["next_id"] += 1
        # add the new bunch of images
        PROJECT["alias"][name] = name
        # only for the first time in features stage: create the new branch
        if not (name in PROJECT["data"]):
            PROJECT["data"][name] = {}
        PROJECT["data"][name][self.stage] = assignDefault(self.stage)
        self.addItem(name, "left")
        self.updateLeftList()
        return

    def delLeft(self):
        item = self.leftList.takeItem(self.leftList.currentRow())
        if item is None:
            return
        del PROJECT["data"][item.data(Qt.Qt.UserRole)][self.stage]
        self.updateLeftList()
        return

    def updateLeftList(self):
        global PROJECT
        for i in range(self.leftList.count()):
            item = self.leftList.item(i)
            PROJECT["alias"][str(item.data(Qt.Qt.UserRole))] = str(item.text())
        if not (self.evt is None):
            self.evt.on_list_change(self)
            
    def addRight(self):
        global PROJECT
        if self.selected == None:
            return
        home = os.path.expanduser(".")
        listn = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                       "Open Images",
                                                       home,
                                                       "Images (*.jpg *.JPG);; All files (*.*)")
        if listn[0] == "":
            return
        # set the item as not computed
        PROJECT["data"][self.selected][self.stage]["state"] = "idle"
        self.evt.on_images_change(self, self.selected, listn[0])
        self.updateRightList()
        return

    def delRight(self):
        global PROJECT
        if (self.selected is None) or (self.rightList.count() <= 0):
            return
        for i in range(self.rightList.count()):
            item = self.rightList.item(i)
            if item.isSelected():
                self.evt.on_remove_image(self.selected, item.text())
        # set the item as not computed
        PROJECT["data"][self.selected][self.stage]["state"] = "idle"
        self.updateRightList()
        return

    def addItem(self, item, nlist="left", alias=None):
        global PROJECT
        newitem = QtWidgets.QListWidgetItem()
        if alias is None:
            alias = item
        newitem.setText(alias)
        newitem.setFlags (newitem.flags () | Qt.Qt.ItemIsEditable)
        if nlist=="left":
            newitem.setData(Qt.Qt.UserRole, item)
            if item not in PROJECT["data"]:
                PROJECT["data"][item] = {}
            if self.stage not in PROJECT["data"][item]:
                PROJECT["data"][item][self.stage] = assignDefault(self.stage)
            
            state = PROJECT["data"][item][self.stage]["state"]
        
            if state == "idle":
                newitem.setForeground(Qt.Qt.red)
            elif state == "waiting":
                newitem.setForeground(Qt.Qt.yellow)
            elif state == "running":
                newitem.setForeground(Qt.Qt.darkYellow)
            elif state == "done":
                newitem.setForeground(Qt.Qt.green)
            else:
                newitem.setForeground(Qt.Qt.magenta)
            self.leftList.addItem(newitem)
        else:
            newitem.setData(Qt.Qt.UserRole, item)
            self.rightList.addItem(newitem)

    def leftDirChanged(self, item):
        if item is None:
            return
        self.selected = item.data(Qt.Qt.UserRole)
        self.updateLeftList()
        self.updateRightList()

    def updateRightList(self):
        global CACHE
        if self.selected is None:
            return

        self.rightList.clear()
        if self.stage == "features":
            base = os.path.dirname(CACHE["current_prj"])
            dirc = os.path.join(base, PROJECT["paths"]["features"])
            dirc = os.path.join(dirc, self.selected)
            for filejpg in os.listdir(dirc):
                if filejpg.endswith(".jpg") or filejpg.endswith(".JPG"):
                    newitem = QtWidgets.QListWidgetItem(self.rightList)
                    iconf = os.path.join(dirc, filejpg)
                    newitem.setIcon(QtGui.QIcon(iconf))
                    newitem.setText(filejpg)
        else:
            if self.stage == "sfm":
                dirc = PROJECT["paths"]["dense_cloud"]
            elif self.stage == "dense_cloud":
                dirc = PROJECT["paths"]["surface"]
            elif self.stage == "surface":
                dirc = PROJECT["paths"]["final"]

            base = os.path.dirname(CACHE["current_prj"])
            dirc = os.path.join(base, dirc)
            dirc = os.path.join(dirc, self.selected)
            if self.stage == "dense_cloud":
                dirc = os.path.join(dirc, "PMVS")
                dirc = os.path.join(dirc, "models")

            if not os.path.isdir(dirc):
                print("No files in " + dirc)
                return
            for fileply in os.listdir(dirc):
                if fileply[0] >= "0" and fileply[0] <= "9": # discard temporal
                    continue
                if (fileply.endswith(".ply") or fileply.endswith(".PLY") or
                    fileply.endswith(".obj") or fileply.endswith(".OBJ") ):
                    newitem = QtWidgets.QListWidgetItem(self.rightList)
                    iconf = os.path.join(dirc, fileply)
                    newitem.setIcon(QtGui.QIcon(iconf))
                    newitem.setText(fileply)
                
    #def leftDirRenamed(self, item):
    #    print("RENAMED TO: "  + item.text())

    def localTask(self):
        if self.selected is None:
            return
        elif self.stage == "features":
            dialog = launcherFeaturesOptions(self)
            dialog.exec_()
        elif self.stage == "sfm":
            dialog = launcherSFMOptions(self)
            dialog.exec_()
        elif self.stage == "dense_cloud":
            dialog = launcherDenseOptions(self)
            dialog.exec_()
        elif self.stage == "surface":
            dialog = launcherSurfaceOptions(self)
            dialog.exec_()
        else:
            print("TODO: localTask")

        #unselect
        self.leftList.selectionModel().reset()
        return

    def remoteTask(self):
        if self.selected is None:
            return
        elif self.stage == "features":
            dialog = launcherFeaturesOptions(self, local = False)
            dialog.exec_()
        elif self.stage == "sfm":
            dialog = launcherSFMOptions(self, local = False)
            dialog.exec_()
        elif self.stage == "dense_cloud":
            dialog = launcherDenseOptions(self)
            dialog.exec_()
        elif self.stage == "surface":
            dialog = launcherSurfaceOptions(self)
            dialog.exec_()
        else:
            print("TODO: remoteTask")

        #unselect
        self.leftList.selectionModel().reset()
        return



    def monitorTasks(self):
        global CACHE,PROJECT
        t = None
        for id in CACHE["local_tasks"]: # get the name of the bunch
            found = False
            for i in range(self.leftList.count()): # list all elements
                item = self.leftList.item(i)
                idlist = item.data(Qt.Qt.UserRole)

                if id == idlist and (self.stage in CACHE["local_tasks"][id]):
                    found = True
                    break
            if not found:
                return

            deleteList = []
            if not(idlist is None):
                waiting = False
                running = False
                canceled = False
                PROJECT["data"][id][self.stage]["state"] = "done"
                deleteList = []

                if CACHE["local_tasks"][id][self.stage] is None:
                    return 
                CACHE["local_task_lock"].acquire()
                for t in CACHE["local_tasks"][id][self.stage]:
                    if t is None:
                        deleteList.append(t)
                    elif t.state == "waiting":
                        waiting = True
                    elif t.state == "running":
                        running = True
                    elif t.state == "aborted":
                        canceled = True
                        deleteList.append(t)
                        for t2 in CACHE["local_tasks"][id][self.stage]:
                            t2.kill()
                        break
                    else: # task is done
                        deleteList.append(t)

                # clean the list of tasks (TODO)
                A = CACHE["local_tasks"][id][self.stage]
                B = deleteList
                CACHE["local_tasks"][id][self.stage] = [x for x in A if x not in B]
                CACHE["local_task_lock"].release()
                
                if running:
                    PROJECT["data"][id][self.stage]["state"] = "running"
                    item.setForeground(Qt.Qt.darkYellow)
                elif canceled:
                    PROJECT["data"][id][self.stage]["state"] = "aborted"
                    item.setForeground(Qt.Qt.red)
                    msgBox = QtWidgets.QMessageBox(self)
                    msgBox.setText("Task aborted [stage " + str(t.pid) + "]")
                    msgBox.exec_()
                elif waiting:
                    PROJECT["data"][id][self.stage]["state"] = "waiting"
                    item.setForeground(Qt.Qt.yellow)
                else:
                    # task has been finished
                    if not(t is None):
                        msgBox = QtWidgets.QMessageBox(self)
                        msgBox.setText(t.name + "Task finished (" + str(t.pid) + ")")
                        msgBox.exec_()
                        PROJECT["data"][id][self.stage]["state"] = "done"
                        item.setForeground(Qt.Qt.green)
                        CACHE["local_tasks"][id][self.stage] = None
                        if not(self.nextPageList is None):
                            self.nextPageList.loadData()

    def viewLeft(self):
        global CACHE,PROJECT
        if self.selected is None:
            return
        if self.stage == "sfm":
            prjdir = os.path.dirname(CACHE["current_prj"])
            mpath = os.path.join(prjdir, PROJECT["paths"]["sfm"])
            mpath = os.path.join(mpath, self.selected)
            view = DialogBrowser(self)
            view = DialogBrowser(parent=self,
                                 title="Matches report for " +
                                 PROJECT["alias"][self.selected])

            path = os.path.join(mpath, "geometric_matches.svg")
            if os.path.isfile(path):
                url = QtCore.QUrl.fromLocalFile(path)
                view.addUrl(url, "Geometric Matches")

            path = os.path.join(mpath, "putative_matches.svg")
            if os.path.isfile(path):
                url = QtCore.QUrl.fromLocalFile(path)
                view.addUrl(url, "Putative Matches")

            path = os.path.join(mpath, "GeometricAdjacencyMatrix.svg")
            if os.path.isfile(path):
                url = QtCore.QUrl.fromLocalFile(path)
                view.addUrl(url, "Geometry Adjacency Matrix")

            path = os.path.join(mpath, "PutativeAdjacencyMatrix.svg")
            if os.path.isfile(path):
                url = QtCore.QUrl.fromLocalFile(path)
                view.addUrl(url, "Putative Adjacency Matrix")

            view.exec_()
        else:
            print("l TODO " + self.stage)
        return

    def viewRight(self):
        if (self.selected is None) or (self.rightList.count() <= 0):
            return

        meshpath = CONFIG["Meshlab/Binaries path"]
        meshpath = os.path.join(meshpath, "meshlab" + CACHE["end_exec"])
        prjdir = os.path.dirname(CACHE["current_prj"])
        if self.stage == "sfm":
            fdir = PROJECT["paths"]["dense_cloud"]
        elif self.stage == "dense_cloud":
            fdir = PROJECT["paths"]["surface"]
        elif self.stage == "surface":
            fdir = PROJECT["paths"]["final"]
        mpath = os.path.join(prjdir, fdir)
        mpath = os.path.join(mpath, self.selected)
        files = False
        filespath = ""

        meshlabConfig = meshlabFile()
        for i in range(self.rightList.count()):
            item = self.rightList.item(i)
            if item.isSelected():
                if self.stage == "dense_cloud":
                    fdir = os.path.join(mpath, "PMVS")
                    fdir = os.path.join(fdir, "models")
                    meshlabConfig.addFile(os.path.join(fdir, item.text()))
                    files = True
                else:
                    meshlabConfig.addFile(os.path.join(mpath, item.text()))
                    files = True
        if files:
            dbase = os.path.dirname(CACHE["current_prj"])
            mfilepath = os.path.join(dbase, "tmp_mesh_file.mlp")
            meshlabConfig.save(mfilepath)
            command = CACHE["prev_exec"] + meshpath + ' "' + mfilepath + '"'
            t = Task()
            t.run(command)
            t.wait()
            if os.path.isfile(mfilepath):
                os.remove(mfilepath)

