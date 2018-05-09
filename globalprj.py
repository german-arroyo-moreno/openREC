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
import os
import threading
from task_manager import *
from configopt import *

def init_cache():
    global CACHE
    CACHE = ConfigOpt()
    # file pointing to the current project file
    CACHE["current_prj"] = None
    CACHE["program_dir"] = os.path.dirname(__file__)
    CACHE["local_tasks"] = {}
    CACHE["local_task_lock"] = threading.Lock()
    if os.system == 'Windows':
        CACHE["prev_exec"] = ""
        CACHE["end_exec"] = ".exe"
        CACHE["all_files"] = "*.*"
    else:
        CACHE["prev_exec"] = "LANG=EN "
        CACHE["end_exec"] = ""
        CACHE["all_files"] = "*"


def killProcess(id=None, stage=None):
    global CACHE
    """
    Kill the process of some id work, in some stage.
    If the stage is None, kill all tasks for some id work.
    If the id is None, kill all process running locally.
    """

    # kill all local processes
    if id is None:
        for id in CACHE["local_tasks"]:
            for stage in CACHE["local_tasks"][id]:
                for t in CACHE["local_tasks"][id][stage]:
                    t.kill()
        CACHE["local_tasks"] = {}
        return True

    # check if id exists
    if not(id in CACHE["local_tasks"]):
        return False

    if stage is None: # kill tasks at all stages
        for id in CACHE["local_tasks"]:
            for stage in CACHE["local_tasks"][id]:
                for t in CACHE["local_tasks"][id][stage]:
                    t.kill()
        CACHE["local_tasks"][id] = {}
    else:
        if not(stage in CACHE["local_tasks"][id]):
            return False
        for t in CACHE["local_tasks"][id][stage]:
            t.kill()
        CACHE["local_tasks"][id][stage] = []

    return True

def init_cfg():
    global CONFIG
    CONFIG = ConfigOpt()
    filen = os.path.join(CACHE["program_dir"], "config.json")
    try:
        CONFIG.open(filen)
    except:
        print("No configuration file found. Setting to default.")
        # server options
        CONFIG["server"] = {}
        CONFIG["server/Last remote task (Advanced option)"] = 1
        CONFIG["server/Address"] = "localhost"
        CONFIG["server/User (optional)"] = ""
        CONFIG["server/Remote path"] = "/tmp"        
        CONFIG["server/NOHUP server path"] = "/usr/bin/"
        # equivalents to local paths but in the server
        CONFIG["server/openMVG"] = {}
        CONFIG["server/openMVG/Binaries path"] = "/usr/local/bin"
        CONFIG["server/openMVG/Database path"] = "/opt/vision/openMVG/src/openMVG/exif/sensor_width_database/sensor_width_camera_database.txt"
        CONFIG["server/CMVS"] = {}
        CONFIG["server/CMVS/Binaries path"] = "/opt/vision/cmvs/program/main/"
        CONFIG["server/Poisson"] = {}
        CONFIG["server/Poisson/Binaries path"] = "/opt/vision/PoissonRecon/Bin/Linux/"
        CONFIG["SSH"] = {}
        CONFIG["SSH/SSH Options"] = "-o ConnectTimeout=10 -o PasswordAuthentication=no -o PreferredAuthentications=publickey -o StrictHostKeyChecking=no"
        CONFIG["SSH/Certificate file (optional)"] = ""
        # local options
        CONFIG["openMVG"] = {}
        CONFIG["openMVG/Binaries path"] = "/usr/local/bin"
        CONFIG["openMVG/Database path"] = "/opt/vision/openMVG/src/openMVG/exif/sensor_width_database/sensor_width_camera_database.txt"
        CONFIG["CMVS"] = {}
        CONFIG["CMVS/Binaries path"] = "/opt/vision/cmvs/program/main/"
        CONFIG["Poisson"] = {}
        CONFIG["Poisson/Binaries path"] = "/opt/vision/PoissonRecon/Bin/Linux/"
        CONFIG["Meshlab"] = {}
        CONFIG["Meshlab/Binaries path"] = "/usr/bin/"
        CONFIG["SSH/Binaries path"] = "/usr/bin/"

def init_prj():
    global PROJECT
    PROJECT = ConfigOpt()
    # default values
    PROJECT["images_stage"] = {}
    PROJECT["sfm_stage"] = {}
    PROJECT["active_process"] = []
    PROJECT["alias"] = {}
    PROJECT["next_id"] = 1
    PROJECT["data"] = {}
    PROJECT["paths"] = {}
    PROJECT["paths"]["features"] = "images"
    PROJECT["paths"]["sfm"] = "matches"
    PROJECT["paths"]["dense_cloud"] = "sfm"
    PROJECT["paths"]["surface"] = "dense_cloud"
    PROJECT["paths"]["final"] = "surface"

def assignDefault(stage):
    v = {}
    if stage == "features":
        v["Camera model"] = "Pinhole radial 3"
        v["Camera internal parameters"] = "Share"
        v["Algorithm for features"] = "SIFT"
        v["Computation or Recomputation"] = "Default"
        v["Upright feature"] = "Rotation invariance"
        v["Image describer"] = "Normal"
        v["Matching ratio"] = 0.8
        v["Model used for robust estimation (matching)"] = "Default" 
        v["Matching method"] = "Fast Cascade Hashing"
        v["Video mode matching"] = "Default"
        v["state"] = "idle" # idle, waiting, running, done
    elif stage == "sfm":
        v["Algorithm"] = "Incremental ACSfm"
        v["Rotation averaging"] = "L2 [Martinec]"
        v["Translation Averaging"] = "Default"
        v["Adjust focal length"] = True
        v["Adjust principal point"] = True
        v["Adjust distortion"] = True
        v["Camera model"] = "Pinhole radial 3"
        v["Scene bundle adjustment"] = False
        v["Residual threshold"] = 4.0
        v["state"] = "idle" # idle, waiting, running, done
    elif stage == "dense_cloud":
        v["Algorithm"] = "PMVS2"
        v["state"] = "idle" # idle, waiting, running, done
    elif stage == "surface":
        v["Algorithm"] = "Poisson [Kazhdan and Hoppe, 2013]"
        v["state"] = "idle" # idle, waiting, running, done
    else:
        print("TODO")
    return v

def incRemoteID():
    global CONFIG
    CONFIG["server/Last remote task (Advanced option)"] += 1
    filen = os.path.join(CACHE["program_dir"], "config.json")
    CONFIG.save(filen)

# ------------------------------------------
# 1. initialize the cache
init_cache()
# 2. initialize the config file
init_cfg()
# 3. initialize the project
init_prj()
# 4. create the task manager
TASK_MANAGER = TaskManager()
# ------------------------------------------
