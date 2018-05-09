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
import shutil
import os.path
        
class launcherFeaturesOptions(QtWidgets.QDialog):
    """
    Local configuration page in preferences.
    CONFIG global variable is required by this class.
    """

    def __init__(self, parent,local=True):
        """
        parent cannot be None
        """ 
        global PROJECT
        super(launcherFeaturesOptions, self).__init__(parent)
        self.parent = parent
        self.local = local

        # extract the parent selected element 
        self.selected_alias = PROJECT["alias/"+self.parent.selected]
        self.selected = self.parent.selected

        if self.local:
            self.setWindowTitle("Managing local task for " + str(self.selected_alias))
        else:
            self.setWindowTitle("Managing remote task for " + str(self.selected_alias))
            
        configGroup = QtWidgets.QLabel("<h2>Features options:</h2>")

        # syncronized with globalprj.py
        v = "data/" + self.selected + "/features"
        self.item = v
        # Check this documentation:
        # http://openmvg.readthedocs.io/en/latest/software/SfM/SfMInit_ImageListing/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeFeatures/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeMatches/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeSfM_DataColor/
        self.algorithm = optionsGroup("Algorithm:",
                                      [
                                          ["Camera model",
                                           PROJECT[v + "/Camera model"],
                                           ["Pinhole","Pinhole radial 1","Pinhole radial 3"]],
                                          ["Camera internal parameters",
                                           PROJECT[v + "/Camera internal parameters"],
                                           ["Do not share","Share"]],
                                          ["Algorithm for features",
                                           PROJECT[v + "/Algorithm for features"],
                                           ["SIFT","AKAZE_FLOAT","AKAZE_MLDB"]],
                                          ["Computation or Recomputation",
                                           PROJECT[v + "/Computation or Recomputation"],
                                           ["Default", "Force recomputing"]],
                                          ["Upright feature",
                                           PROJECT[v + "/Upright feature"],
                                           ["Rotation invariance","Extract orientation angle"]],
                                          ["Image describer",
                                           PROJECT[v + "/Image describer"],
                                           ["Normal","High", "ULTRA (time comsuming)"]],
                                          ["Matching ratio",
                                           PROJECT[v + "/Matching ratio"], 0, 1000, 0.2],
                                          ["Model used for robust estimation (matching)",
                                           PROJECT[v + "/Model used for robust estimation (matching)"],
                                           ["Default", "Fundamental matrix", "Essential matrix", "Homography matrix"]],
                                          ["Matching method",
                                           PROJECT[v + "/Matching method"],
                                           ["Auto", "Brute Force 2", "Approximate Nearest Neighbor L2", "Cascade Hashing", "Fast Cascade Hashing", "Brute Force Hamming"]],
                                          ["Video mode matching",
                                           PROJECT[v + "/Video mode matching"],
                                           ["Default", "0 with (1->X)", "0 with (1,2), 1 with (2,3)...", "0 with (1,2,3), 1 with (2,3,4)..."]]
 
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
        global CACHE,PROJECT,CONFIG
        prjdir = os.path.dirname(CACHE["current_prj"])
        mpath = os.path.join(prjdir, PROJECT["paths"]["sfm"])
        mpath = os.path.join(mpath, self.selected)
        # Clean previous files and create defaults dirs/files:
        if not os.path.exists(mpath):
            os.makedirs(mpath)
        f = open(os.path.join(mpath, "task1_output.txt"), "w")
        f.close()
        f = open(os.path.join(mpath, "task2_output.txt"), "w")
        f.close()
        f = open(os.path.join(mpath, "task3_output.txt"), "w")
        f.close()
        f = open(os.path.join(mpath, "task1_error.txt"), "w")
        f.close()
        f = open(os.path.join(mpath, "task2_error.txt"), "w")
        f.close()
        f = open(os.path.join(mpath, "task3_error.txt"), "w")
        f.close()
        
            
        # -------------------------------------------------
        # 1. SFM Initialization step: Image Listing
        command = "openMVG_main_SfMInit_ImageListing"
        command += CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        inputdir = os.path.join(prjdir, PROJECT["paths"]["features"])
        inputdir = os.path.join(inputdir, self.selected)

        localDirInput = ""
        localDirInput1 = ""
        localDirInput2 = ""
        localDirInput3 = ""
        localDirOutput = ""
        if self.local:
            command += ' -i "' + inputdir + '"' # images path
            command += ' -o "' + mpath + '"' # output path
        else:
            t1 = Task()
            t1_id = t1.newRemoteID()
            localDirInput = inputdir
            remoteInputDir = t1.remote_path + '/input'
            command  += ' -i "' + remoteInputDir + '"'
            localDirOutput = mpath
            remoteOutputDir =  t1.remote_path + '/output'
            command += ' -o "' + remoteOutputDir + '"' # output path

        # Copy the database to the local input directory if the file is not there
        databaseDir = os.path.join(inputdir, "database")
        databaseFile = os.path.join(databaseDir, "database.txt")
        try:
            os.mkdir(databaseDir)
            shutil.copy2(CONFIG["openMVG/Database path"], databaseFile)
        except:
            print("Directory '" + databaseDir + "' already exists.")

        if self.local:
            command += ' -d "' + databaseFile + '"' # path to camera features
        else:
            command += ' -d "' + remoteInputDir + '/database/database.txt"'

        # ignored: -f, -k
        if PROJECT[self.item + "/Camera model"] == "Pinhole":
            command += " -c 1" 
        elif PROJECT[self.item + "/Camera model"] == "Pinhole radial 1":
            command += " -c 2" 
        else:
            command += " -c 3"

        if PROJECT[self.item + "/Camera internal parameters"] != "Share":
            command += " -g 0"
            
        print("1. EXECUTE:")
        print("   " + command)

        # create the list of task for this bunch if doesn't exist
        """
        if not(self.selected in CACHE["local_tasks"]):
            CACHE["local_tasks"][self.selected] = {}
        # create the list of task for this stage if doesn't exist
        if not("features" in CACHE["local_tasks"][self.selected]):
            CACHE["local_tasks"][self.selected]["features"] = []
        """
        if self.local:
            t1 = Task(CACHE["prev_exec"] + command,
                      os.path.join(mpath, "task1_output.txt"),
                      os.path.join(mpath, "task1_error.txt"))
            t1.name = "[Init. features in " + self.selected_alias +  "]"
            """
            CACHE["local_task_lock"].acquire()
            if CACHE["local_tasks"][self.selected]["features"] is None:
                CACHE["local_tasks"][self.selected]["features"] = []
            CACHE["local_tasks"][self.selected]["features"].append(t1)
            CACHE["local_task_lock"].release()
            """
        else:
            t1.command = command
            t1.name = "[Init. features in " + self.selected_alias +  "]"

        a = [(localDirInput, "input")]
        b = (localDirOutput, "output")
        TASK_MANAGER.addTask(t1, local=self.local,
                             localDirInput=a,
                             localDirOutput=b)

        # -------------------------------------------------        
        # 2. Compute features
        command = "openMVG_main_ComputeFeatures"
        command += CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        inputdir = os.path.join(mpath, "sfm_data.json")
        if self.local:
            command += ' -i "' + inputdir + '"' # images path
            command += ' -o "' + mpath + '"' # output dir
        else:
            t2 = Task()
            t2.assignRemoteID(t1_id) # the folder must have the same name as task1
            # require images
            localDirInput1 = os.path.join(prjdir, PROJECT["paths"]["features"])
            localDirInput1 = os.path.join(localDirInput1, self.selected)
            # require the json file
            localDirInput2 = inputdir
            remoteInputDir = t2.remote_path  + "/sfm_data.json"
            remoteOutputDir = t2.remote_path  + "/output"
            command += ' -i "' + remoteInputDir + '"'
            command += ' -o "' + remoteOutputDir + '"'
            
        if PROJECT[self.item + "/Computation or Recomputation"] == "Force recomputing":
            command += " -f 1"

        if PROJECT[self.item + "/Algorithm for features"] == "AKAZE_FLOAT":
            command += " -m AZAKE_FLOAT"
        elif PROJECT[self.item + "/Algorithm for features"] == "AKAZE_MLDB":
            command += " -m AZAKE_MLDB"
        else:
            command += " -m SIFT"

        if PROJECT[self.item + "/Upright feature"] == "Extract orientation angle":
            command += " -u 1"

        if PROJECT[self.item + "/Image describer"] == "High":
            command += " -p HIGH"
        elif PROJECT[self.item + "/Image describer"] == "ULTRA (time comsuming)":
            command += " -p ULTRA"

       
        print("2. EXECUTE:")
        print("   " + command)
        if self.local:
            t2 = Task(CACHE["prev_exec"] + command,
                      os.path.join(mpath, "task2_output.txt"),
                      os.path.join(mpath, "task2_error.txt"))
            t2.name = "[Dectecting features in " + self.selected_alias +  "]"
            """
            CACHE["local_task_lock"].acquire()
            CACHE["local_tasks"][self.selected]["features"].append(t2)
            CACHE["local_task_lock"].release()
            """
            #f2 = lambda task, code: t2.run(evtfunc=self.monitorThreads) if not code else print("ERROR in TASK 1")
            #t1.addStopEvent(f2)
        else:
            t2.name = "[Dectecting features in " + self.selected_alias +  "]"
            t2.command = command

        a = [(localDirInput1, "input"), (localDirInput2, "sfm_data.json")]
        b = (localDirOutput, "output")
        TASK_MANAGER.addTaskDependOnTask(t2, t1, local=self.local,
                                         localDirInput = a,
                                         localDirOutput = b)
            
        
        # -------------------------------------------------        
        # 3. Compute matches
        command = "openMVG_main_ComputeMatches"
        command += CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        inputdir = os.path.join(mpath, "sfm_data.json")
        if self.local:
            command += ' -i "' + inputdir + '"' # images path
            command += ' -o "' + mpath + '"' # output dir
        else:
            t3 = Task()
            t3.assignRemoteID(t1_id)
            # require images
            localDirInput3 = localDirInput1
            # require the features
            localDirInput1 = mpath
            # require the json file
            localDirInput2 = inputdir
            remoteInputDir = t3.remote_path  + "/sfm_data.json"
            remoteOutputDir = t3.remote_path  + "/output"
            command += ' -i "' + remoteInputDir + '"'
            command += ' -o "' + remoteOutputDir + '"'

        if PROJECT[self.item + "/Computation or Recomputation"] == "Force recomputing":
            command += " -f 1"

        if PROJECT[self.item + "/Matching ratio"] != 0.8:
            command += " -r " + str(PROJECT[self.item + "/Matching ratio"])

        if PROJECT[self.item + "/Model used for robust estimation (matching)"] == "Fundamental matrix":
            command += " -g f" 
        elif PROJECT[self.item + "/Model used for robust estimation (matching)"] == "Essential matrix":
            command += " -g e" 
        elif PROJECT[self.item + "/Model used for robust estimation (matching)"] == "Homography matrix":
            command += " -g h" 

        if PROJECT[self.item + "/Matching method"] == "Brute Force 2":
            command += " -n BRUTEFORCEL2" 
        elif PROJECT[self.item + "/Matching method"] == "Approximate Nearest Neighbor L2":
            command += " -n ANNL2"
        elif PROJECT[self.item + "/Matching method"] == "Cascade Hashing":
            command += " -n CASCADEHASHINGL2"
        elif PROJECT[self.item + "/Matching method"] == "Fast Cascade Hashing":
            command += " -n FASTCASCADEHASHINGL2"
        elif PROJECT[self.item + "/Matching method"] == "Brute Force Hamming":
            command += " -n BRUTEFORCEHAMMING"
        else:
            command += " -n AUTO"

        if PROJECT[self.item + "/Video mode matching"] == "0 with (1->X)":
            command += " -v X"
        elif PROJECT[self.item + "/Video mode matching"] == "0 with (1,2), 1 with (2,3)...":
            command += " -v 2"
        elif PROJECT[self.item + "/Video mode matching"] == "0 with (1,2,3), 1 with (2,3,4)...":
            command += " -v 3"
        
        print("3. EXECUTE:")
        print("   " + command)

        if self.local:
            t3 = Task(CACHE["prev_exec"] + command,
                      os.path.join(mpath, "task3_output.txt"),
                      os.path.join(mpath, "task3_error.txt"))
            t3.name = "[Matching features in " + self.selected_alias +  "]"
            """
            CACHE["local_task_lock"].acquire()
            CACHE["local_tasks"][self.selected]["features"].append(t3)
            CACHE["local_task_lock"].release()
            """
            #f3 = lambda task, code: t3.run(evtfunc=self.monitorThreads) if not code else print("ERROR in TASK 2")
            #t2.addStopEvent(f3)
        
            #t1.run(evtfunc=self.monitorThreads)
        else:
            t3.name = "[Matching features in " + self.selected_alias +  "]"
            t3.command = command
            
        a = [(localDirInput1, "output"), (localDirInput2, "sfm_data.json"), (localDirInput3, "input")]
        b = (localDirOutput, "output")
        TASK_MANAGER.addTaskDependOnTask(t3, t2, local=self.local,
                                         localDirInput = a,
                                         localDirOutput = b)
        
        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks attached to " + self.selected_alias + " (images) have been launched at background.");
        msgBox.exec_()

    def cancelTask(self):
        global PROJECT
        killProcess(id=self.selected, stage="features")
        PROJECT["data"][self.selected]["features"]["state"] = "aborted"
        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks canceled " + self.selected_alias + " (images).");
        msgBox.exec_()

    def launchWeb(self, filen):
        global CACHE,PROJECT
        #url = QtCore.QUrl("file://" + filen)
        prjdir = os.path.dirname(CACHE["current_prj"])
        mpath = os.path.join(prjdir, PROJECT["paths"]["sfm"])
        mpath = os.path.join(mpath, self.selected)

        view = DialogBrowser(self)

        path = os.path.join(mpath, "task1_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "1. Initializing")

        path = os.path.join(mpath, "task2_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "2. Detecting features")
        
        path = os.path.join(mpath, "task3_output.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "3. Matching features")
        
        path = os.path.join(mpath, "task1_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "A. Errors when initializing")        

        path = os.path.join(mpath, "task2_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "B. Errors when detecting features")

        path = os.path.join(mpath, "task3_error.txt")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "C. Errors when matching features")

        """
        path = os.path.join(mpath, "geometric_matches.svg")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "Geometric Matches")
        path = os.path.join(mpath, "putative_matches.svg")
        url = QtCore.QUrl.fromLocalFile(path)
        view.addUrl(url, "Putative Matches")
        """
        view.exec_()

