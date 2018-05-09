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
from webBrowser import * 
from optionsGroup import *
from globalprj import *
from task import *

try:
    from psutil import cpu_count
    NCPUS = cpu_count(logical=True)
except:
    NCPUS = 1
    
class launcherSurfaceOptions(QtWidgets.QDialog):
    """
    Local configuration page in preferences.
    CONFIG global variable is required by this class.
    """

    def __init__(self, parent):
        """
        parent cannot be None
        """ 
        global PROJECT
        super(launcherSurfaceOptions, self).__init__(parent)
        self.parent = parent

        # extract the parent selected element 
        self.selected_alias = PROJECT["alias/"+self.parent.selected]
        self.selected = self.parent.selected

        self.setWindowTitle("Managing task for " + str(self.selected_alias))
        configGroup = QtWidgets.QLabel("<h2>Structure from Motion options:</h2>")

        # syncronized with globalprj.py
        v = "data/" + self.selected + "/surface"
        self.item = v
        # https://github.com/mkazhdan/PoissonRecon
        self.algorithm = optionsGroup("Algorithm:",
                                      [
                                          ["Algorithm",
                                           PROJECT[v + "/Algorithm"],
                                           ["Poisson [Kazhdan and Hoppe, 2013]"]],
                                      ],
                                      self.updateOptions)


        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.algorithm)
        mainLayout.addStretch(1)

        # Add the buttons
        buttonsLayout = QtWidgets.QHBoxLayout()
        closeButton = QtWidgets.QPushButton("&Back")
        closeButton.clicked.connect(self.close_application)
        buttonsLayout.addWidget(closeButton)

        if (PROJECT[self.item + "/state"] == "idle" or
            PROJECT[self.item + "/state"] == "done"):
            runButton = QtWidgets.QPushButton("Run Task")
            runButton.clicked.connect(self.runTask)
            buttonsLayout.addWidget(runButton)
            reportButton = QtWidgets.QPushButton("Display last report")
            reportButton.clicked.connect(self.launchWeb)
            buttonsLayout.addWidget(reportButton)
        elif (PROJECT[self.item + "/state"] == "waiting" or
              PROJECT[self.item + "/state"] == "running"):
            cancelButton = QtWidgets.QPushButton("Cancel Current Task")
            cancelButton.clicked.connect(self.cancelTask)
            buttonsLayout.addWidget(cancelButton)
            reportButton = QtWidgets.QPushButton("Display current report")
            reportButton.clicked.connect(self.launchWeb)
            buttonsLayout.addWidget(reportButton)

        mainLayout.addLayout(buttonsLayout)
        
        self.setLayout(mainLayout)
        return

    def updateOptions(self, var):
        global PROJECT,CACHE
        PROJECT[self.item] = ConfigOpt.merge(PROJECT[self.item], var)
        PROJECT.save(CACHE["current_prj"])

    def close_application(self):
        self.close()

    def runTask(self):
        global CACHE,PROJECT,CONFIG,TASK_MANAGER
        prjdir = os.path.dirname(CACHE["current_prj"])
        opath = os.path.join(prjdir, PROJECT["paths"]["final"])
        opath = os.path.join(opath, self.selected)
        # Clean previous files and create defaults dirs/files:
        if not os.path.exists(opath):
            os.makedirs(opath)
        f = open(os.path.join(opath, "task1_output.txt"), "w")
        f.close()
        f = open(os.path.join(opath, "task2_output.txt"), "w")
        f.close()
        f = open(os.path.join(opath, "task3_output.txt"), "w")
        f.close()
        f = open(os.path.join(opath, "task1_error.txt"), "w")
        f.close()
        f = open(os.path.join(opath, "task2_error.txt"), "w")
        f.close()
        f = open(os.path.join(opath, "task3_error.txt"), "w")
        f.close()

        # -------------------------------------------------
        # 1. Convert settings first
        if PROJECT[self.item + "/Algorithm"] == "Poisson [Kazhdan and Hoppe, 2013]":
            command = "PoissonRecon"
        else:
            print("TODO launcherSurfaceOptions: " + PROJECT[self.item + "/Algorithm"])
            return
        command += CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["Poisson/Binaries path"], command)

        # input from previous stage
        inputdir = os.path.join(prjdir, PROJECT["paths"]["surface"]) # matches dir
        mpath = os.path.join(inputdir, self.selected)
        inputdir = os.path.join(mpath, "PMVS")
        inputdir = os.path.join(inputdir, "models")
        inputdir = os.path.join(inputdir, "pmvs_options.txt.pset")

        dependant_files = [inputdir]

        ofile = os.path.join(opath, "final.ply")
        if PROJECT[self.item + "/Algorithm"] == "Poisson [Kazhdan and Hoppe, 2013]":
            command += ' --in "' + inputdir + '"' # images path
            command += '  --out "' + ofile + '"' # output path
            command += "  --depth 10 --verbose --threads " + str(NCPUS)
        print("1. EXECUTE:")
        print("   " + command)

        # create the list of task for this bunch if doesn't exist
        """
        if not(self.selected in CACHE["local_tasks"]):
            CACHE["local_tasks"][self.selected] = {}
        # create the list of task for this stage if doesn't exist
        if not("surface" in CACHE["local_tasks"][self.selected]):
            CACHE["local_tasks"][self.selected]["surface"] = []
        """
        t1 = Task(CACHE["prev_exec"] + command,
                  os.path.join(opath, "task1_output.txt"),
                  os.path.join(opath, "task1_error.txt"))
        t1.name = "[Reconstructing surface in " + self.selected_alias +  "]"
        """
        CACHE["local_task_lock"].acquire()
        if CACHE["local_tasks"][self.selected]["surface"] is None:
            CACHE["local_tasks"][self.selected]["surface"] = []
        CACHE["local_tasks"][self.selected]["surface"].append(t1)
        CACHE["local_task_lock"].release()
        """
        # -------------------------------------------------        
        # 2. Construct a dense cloud
        command = "meshlabserver"
        command += CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["Meshlab/Binaries path"], command)

        ofile2 = os.path.join(prjdir, PROJECT["paths"]["surface"])
        ofile2 = os.path.join(ofile2, self.selected)
        ofile2 = os.path.join(ofile2, "PMVS")
        ofile2 = os.path.join(ofile2, "models")
        ofile2 = os.path.join(ofile2, "pmvs_options.txt.ply")

        ofileC = os.path.join(opath, "final_color.obj")

        pathScript = os.path.dirname(sys.argv[0])
        pathScript = os.path.join(pathScript, "meshlab-script")
        pathScript = os.path.join(pathScript, "transfer_color.mlx")
        # first the color, then the surface
        command += ' -i "' + ofile2 + '" "' + ofile + '"'
        command += ' -s "' + pathScript + '"'
        command += ' -o "' + ofileC + '"'
        command += " -om vc fq wn"

        print("2. EXECUTE:")
        print("   " + command)

        t2 = Task(CACHE["prev_exec"] + " " + command,
                  os.path.join(opath, "task2_output.txt"),
                  os.path.join(opath, "task2_error.txt"))
        t2.name = "[Coloring surface in " + self.selected_alias +  "]"
        """
        CACHE["local_task_lock"].acquire()
        CACHE["local_tasks"][self.selected]["surface"].append(t2)
        CACHE["local_task_lock"].release()
        """
        #f2 = lambda task, code: t2.run(evtfunc=self.monitorThreads) if not code  else print("ERROR in TASK 1")
        #t1.addStopEvent(f2)

        #t1.run(evtfunc=self.monitorThreads)
        TASK_MANAGER.addTaskDependOnFiles(t1, dependant_files)
        TASK_MANAGER.addTaskDependOnTask(t2, t1)

        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks attached to " + self.selected_alias + " (Dense reconstruction) have been launched at background.");
        msgBox.exec_()

    def cancelTask(self):
        global PROJECT
        killProcess(id=self.selected, stage="surface")
        PROJECT["data"][self.selected]["surface"]["state"] = "aborted"
        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks canceled " + self.selected_alias + " (images).");
        msgBox.exec_()

    def launchWeb(self, filen):
        global CACHE,PROJECT
        #url = QtCore.QUrl("file://" + filen)
        prjdir = os.path.dirname(CACHE["current_prj"])
        mpath = os.path.join(prjdir, PROJECT["paths"]["final"])
        mpath = os.path.join(mpath, self.selected)
        print(mpath)
        view = DialogBrowser(self)

        path = os.path.join(mpath, "task1_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "1. Do reconstruction")

        path = os.path.join(mpath, "task2_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "2. Colorize structure")
        
        path = os.path.join(mpath, "task3_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "3. Robust triangulation")
        
        path = os.path.join(mpath, "task1_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "A. Errors when reconstructing")        

        path = os.path.join(mpath, "task2_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "B. Errors when colorizing")

        path = os.path.join(mpath, "task3_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "C. Errors when triangulating")

        view.exec_()

