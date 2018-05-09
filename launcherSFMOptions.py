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
import tools

class launcherSFMOptions(QtWidgets.QDialog):
    """
    Local configuration page in preferences.
    CONFIG global variable is required by this class.
    """

    def __init__(self, parent, local=True):
        """
        parent cannot be None
        """ 
        global PROJECT
        super(launcherSFMOptions, self).__init__(parent)
        self.parent = parent
        self.local = local

        # extract the parent selected element 
        self.selected_alias = PROJECT["alias/"+self.parent.selected]
        self.selected = self.parent.selected

        if self.local:
            self.setWindowTitle("Managing local task for " + str(self.selected_alias))
        else:
            self.setWindowTitle("Managing remote task for " + str(self.selected_alias))

        configGroup = QtWidgets.QLabel("<h2>Structure from Motion options:</h2>")

        # syncronized with globalprj.py
        v = "data/" + self.selected + "/sfm"
        self.item = v
        # Check this documentation:
        # http://openmvg.readthedocs.io/en/latest/software/SfM/SfMInit_ImageListing/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeFeatures/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeMatches/
        # http://openmvg.readthedocs.io/en/latest/software/SfM/ComputeSfM_DataColor/
        self.algorithm = optionsGroup("Algorithm:",
                                      [
                                          ["Algorithm",
                                           PROJECT[v + "/Algorithm"],
                                           ["Global ACSfm","Incremental ACSfm"]], # SfM
                                          ["Adjust focal length",
                                           PROJECT[v + "/Adjust focal length"], # SfM
                                           "BOOL"],
                                          ["Adjust principal point",
                                           PROJECT[v + "/Adjust principal point"], # SfM
                                           "BOOL"],
                                          ["Adjust distortion",
                                           PROJECT[v + "/Adjust distortion"], # SfM
                                           "BOOL"],
                                          ["Scene bundle adjustment", # openMVG_main_ComputeStructureFromKnownPoses
                                           PROJECT[v + "/Bundle adjustment"],
                                           "BOOL"],
                                          ["Residual threshold", # openMVG_main_ComputeStructureFromKnownPoses
                                           PROJECT[v + "/Residual threshold"],
                                           0, 100, 0.1]
                                      ],
                                      self.updateAlgorithm)

        # http://openmvg.readthedocs.io/en/latest/software/SfM/GlobalSfM/
        self.gacsfm = optionsGroup("Global ACSfM:",
                                   [
                                       ["Rotation averaging",
                                        PROJECT[v + "/Rotation averaging"],
                                        ["L1 [Chatterjee]","L2 [Martinec]"]],
                                       ["Translation Averaging",
                                        PROJECT[v + "/Translation Averaging"],
                                        ["Default","L1 [GlobalACSfM]","L2 [Kyle2014]", "SoftL1 minimization [GlobalACSfM]"]]
                                   ],
                                   self.updateOptions)

        # http://openmvg.readthedocs.io/en/latest/software/SfM/IncrementalSfM/
        # ignored: -a, -b        
        self.iacsfm = optionsGroup("Incremental ACSfM:",
                                  [
                                      ["Camera model",
                                       PROJECT[v + "/Camera model"],
                                       ["Pinhole","Pinhole radial 1","Pinhole radial 3","Pinhole radial 3 + tangencial 2", "Pinhole fisheye"]]
                                  ],
                                  self.updateOptions)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.algorithm)
        mainLayout.addWidget(self.iacsfm)
        mainLayout.addWidget(self.gacsfm)
        mainLayout.addStretch(1)

        if PROJECT[self.item]["Algorithm"] == "Incremental ACSfm":
            self.iacsfm.setEnabled(True)
            self.gacsfm.setEnabled(False)
        else:
            self.iacsfm.setEnabled(False)
            self.gacsfm.setEnabled(True)

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

    def updateAlgorithm(self, var):
        global PROJECT,CACHE
        PROJECT[self.item] = ConfigOpt.merge(PROJECT[self.item], var)
        PROJECT.save(CACHE["current_prj"])

        if PROJECT[self.item]["Algorithm"] == "Incremental ACSfm":
            self.iacsfm.setEnabled(True)
            self.gacsfm.setEnabled(False)
        else:
            self.iacsfm.setEnabled(False)
            self.gacsfm.setEnabled(True)
        print("updateAlgorithm sfm")

    def close_application(self):
        self.close()

    def runTask(self):
        global CACHE,PROJECT,CONFIG,TASK_MANAGER
        prjdir = os.path.dirname(CACHE["current_prj"])
        opath = os.path.join(prjdir, PROJECT["paths"]["dense_cloud"])
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
        # 1. ACSfM step
        tmp_command = ""
        if PROJECT[self.item + "/Algorithm"] == "Incremental ACSfm":
            tmp_command = "openMVG_main_IncrementalSfM"
        else:
            tmp_command = "openMVG_main_GlobalSfM"
        command = tmp_command + CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        # input from previous stage
        inputdir = os.path.join(prjdir, PROJECT["paths"]["sfm"]) # matches dir
        mpath = os.path.join(inputdir, self.selected)
        inputdir = os.path.join(mpath, "sfm_data.json")

        localDirInput = os.path.join(prjdir, PROJECT["paths"]["features"]) # images
        localDirInput = os.path.join(localDirInput, self.selected)
        localDirMatch = mpath
        localDirOutput = opath
        remoteDirInput = ""
        remoteDirMatch = ""
        remoteDirOutput = ""

        if self.local:
            command += ' -i "' + inputdir + '"' # images path
            command += ' -m "' + mpath + '"' # match points path
            command += ' -o "' + opath + '"' # output path
            # Point JSON FILE to local directory:
            jsonChange = (inputdir, inputdir, localDirInput)
        else:
            # Create a remote task and assign the local paths
            t = Task()
            t.newRemoteID()
            rcommand = CONFIG["server/openMVG/Binaries path"] + "/" + tmp_command
            remoteDirMatch = t.remote_path + "/match"
            remoteDirOutput = t.remote_path + "/output"
            rcommand += ' -i "' + remoteDirMatch + '/sfm_data.json"'
            rcommand += ' -m "' + remoteDirMatch  + '"'
            rcommand += ' -o "' + remoteDirOutput + '"'
            # Point JSON FILE to remote directory:
            jsonChange = (inputdir, inputdir, t.remote_path + "/input")

        # Define the dependant files for the local task
        dependant_files = [inputdir]
        ldir = os.path.join(prjdir, PROJECT["paths"]["features"])
        ldir = os.path.join(ldir, self.selected)
        ldir2 = os.path.join(prjdir, PROJECT["paths"]["sfm"])
        ldir2 = os.path.join(ldir2, self.selected)
        ldir = tools.requiredFilesForSFM(ldir, ldir2)
        dependant_files.extend(ldir)

        tmp_command = ""
        if PROJECT[self.item + "/Algorithm"] == "Incremental ACSfm":
            # ignored: -a, -b
            if PROJECT[self.item + "/Camera model"] == "Pinhole":
                tmp_command += " -c 1"
            elif PROJECT[self.item + "/Camera model"] == "Pinhole radial 1":
                tmp_command += " -c 2"
            elif PROJECT[self.item + "/Camera model"] == "Pinhole radial 3":
                tmp_command += "" # default
            elif PROJECT[self.item + "/Camera model"] == "Pinhole radial 3 + tangencial 2":
                tmp_command += " -c 4"
            elif PROJECT[self.item + "/Camera model"] == "Pinhole fisheye":
                tmp_command += " -c 5"
        else: # GlobalACSfM
            if PROJECT[self.item + "/Rotation averaging"] == "L1 [Chatterjee]":
                tmp_command += " -r 1"
            if PROJECT[self.item + "/Translation Averaging"] == "L1 [GlobalACSfM]":
                tmp_command += " -t 1"
            elif PROJECT[self.item + "/Translation Averaging"] == "L2 [Kyle2014]":
                tmp_command += " -t 2"
            elif PROJECT[self.item + "/Translation Averaging"] == "SoftL1 minimization [GlobalACSfM]":
                tmp_command += " -t 3"

        if self.local: # complete the command
            command += tmp_command
        else:
            rcommand += tmp_command

        # Parameters for both SfM algorithms
        adjustlist = []
        if PROJECT[self.item + "/Adjust focal length"] == True:
            adjustlist.append("ADJUST_FOCAL_LENGTH")
        if PROJECT[self.item + "/Adjust principal point"] == True:
            adjustlist.append("ADJUST_PRINCIPAL_POINT")
        if PROJECT[self.item + "/Adjust distortion"] == True:
            adjustlist.append("ADJUST_DISTORTION")

        tmp_command = ""
        if len(adjustlist) == 0: # no flag is activated
            tmp_command += " -f NONE"
        elif len(adjustlist) < 3: # all flags are not activated
            opt = adjustlist[0]
            for e in adjustlist[1:]:
                opt += "|" + e
            tmp_command += " -f " + opt

        if self.local:
            command += tmp_command
        else:
            rcommand += tmp_command

        print("1. EXECUTE:")
        print("   " + command)

        if self.local:
            # create the list of task for this bunch if doesn't exist
            """
            if not(self.selected in CACHE["local_tasks"]):
                CACHE["local_tasks"][self.selected] = {}
                # create the list of task for this stage if doesn't exist
                if not("sfm" in CACHE["local_tasks"][self.selected]):
                    CACHE["local_tasks"][self.selected]["sfm"] = []
            """
            t1 = Task(CACHE["prev_exec"] + command,
                      os.path.join(opath, "task1_output.txt"),
                      os.path.join(opath, "task1_error.txt"))
            t1.name = "[Init. SfM in " + self.selected_alias +  "]"
            t1.jsonChange = jsonChange
            """
            CACHE["local_task_lock"].acquire()
            if self.selected not in CACHE["local_tasks"]:
                CACHE["local_tasks"][self.selected] = {}
            if "sfm" not in CACHE["local_tasks"][self.selected]:
                CACHE["local_tasks"][self.selected]["sfm"] = []
            CACHE["local_tasks"][self.selected]["sfm"].append(t1)
            CACHE["local_task_lock"].release()
            """
        # -------------------------------------------------
        # 2. Colorize the structure
        tmp_command = "openMVG_main_ComputeSfM_DataColor"
        command = tmp_command + CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        if self.local == False:
            rcommand += " && " + CONFIG["server/openMVG/Binaries path"] + "/" + tmp_command

        inputdir = os.path.join(opath, "sfm_data.bin")
        outputf = os.path.join(opath, "colorized.ply")
        command += ' -i "' + inputdir + '"' # images path
        command += ' -o "' + outputf + '"' # output dir 

        if self.local == False:
            rcommand += ' -i "' + remoteDirOutput + '/sfm_data.bin"'
            rcommand += ' -o "' + remoteDirOutput + '/colorized.ply"'

        if self.local:
            print("2. EXECUTE:")
            print("   " + command)
            t2 = Task(CACHE["prev_exec"] + command,
                      os.path.join(opath, "task2_output.txt"),
                      os.path.join(opath, "task2_error.txt"))
            t2.name = "[Dectecting SfM in " + self.selected_alias +  "]"
            t2.jsonChange = jsonChange
            """
            CACHE["local_task_lock"].acquire()
            CACHE["local_tasks"][self.selected]["sfm"].append(t2)
            CACHE["local_task_lock"].release()
            """
            #f2 = lambda task, code: t2.run(evtfunc=self.monitorThreads) if not code  else print("ERROR in TASK 1")
            #t1.addStopEvent(f2)

        # -------------------------------------------------        
        # 3. Structure from Known Poses (robust triangulation)
        tmp_command = "openMVG_main_ComputeStructureFromKnownPoses"
        command = tmp_command + CACHE["end_exec"] # if not posix
        command = os.path.join(CONFIG["openMVG/Binaries path"], command)

        if self.local == False:
            rcommand += " && " + CONFIG["server/openMVG/Binaries path"] + "/" + tmp_command

        # -f, -p ignored
        inputdir = os.path.join(opath, "sfm_data.bin")
        outputf = os.path.join(opath, "robust.ply")
        if self.local:
            command += ' -i "' + inputdir + '"' # images path
            command += ' -m "' + mpath + '"' # match points path
            command += ' -o "' + outputf + '"' # output dir
        else:
            rcommand += ' -i "' + remoteDirOutput + '/sfm_data.bin"' # images path
            rcommand += ' -m "' + remoteDirMatch + '"' # match points path
            rcommand += ' -o "' + remoteDirOutput + '/robust.ply"' # output dir

        if PROJECT[self.item + "/Scene bundle adjustment"]:
            command += " -b"

        if PROJECT[self.item + "/Residual threshold"] != 0.4:
            command += " -r " + str(PROJECT[self.item + "/Residual threshold"])

        if self.local:
            print("3. EXECUTE:")
            print("   " + command)
            if self.local:
                t3 = Task(CACHE["prev_exec"] + command,
                          os.path.join(opath, "task3_output.txt"),
                          os.path.join(opath, "task3_error.txt"))
                t3.name = "[Matching SfM in " + self.selected_alias +  "]"
                t3.jsonChange = jsonChange
                """
                CACHE["local_task_lock"].acquire()
                CACHE["local_tasks"][self.selected]["sfm"].append(t3)
                CACHE["local_task_lock"].release()
                """
                #f3 = lambda task, code: t3.run(evtfunc=self.monitorThreads) if not code else print("ERROR in TASK 2")
                #t2.addStopEvent(f3)

                #t1.run(evtfunc=self.monitorThreads)
                TASK_MANAGER.addTaskDependOnFiles(t1,dependant_files)
                TASK_MANAGER.addTaskDependOnTask(t2, t1)
                TASK_MANAGER.addTaskDependOnTask(t3, t2)
        else: # remote task launcher
            t.command = rcommand
            t.jsonChange = jsonChange
            a = [(localDirInput, "input"), (localDirMatch, "match")]
            b = (localDirOutput, "output")
            TASK_MANAGER.addTaskDependOnFiles(t, dependant_files,
                                              local=False,
                                              localDirInput=a,
                                              localDirOutput=b)
        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks attached to " + self.selected_alias + " (SfM) have been launched at background.");
        msgBox.exec_()

    def cancelTask(self):
        global PROJECT
        killProcess(id=self.selected, stage="sfm")
        PROJECT["data"][self.selected]["sfm"]["state"] = "aborted"
        self.close()
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setText("Tasks canceled " + self.selected_alias + " (images).");
        msgBox.exec_()

    def launchWeb(self, filen):
        global CACHE,PROJECT
        #url = QtCore.QUrl("file://" + filen)
        prjdir = os.path.dirname(CACHE["current_prj"])
        mpath = os.path.join(prjdir, PROJECT["paths"]["dense_cloud"])
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

