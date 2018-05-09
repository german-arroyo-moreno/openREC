# -*- coding: utf-8 -*-
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
import time
import subprocess
import threading
import os, getpass, signal
from globalprj import *
import tools

# create a method to transfer files between this computer and the remote
if os.name == 'posix':
    def pid_exists(pid):
        """Check whether pid exists in the current process table."""
        import errno
        if pid < 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True
else:
    def pid_exists(pid):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x100000

        process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        else:
            return False

class Task:
    """
    This class define all operations to manage a local or
    remote (via SSH) command.

    self.state = "waiting", "running", "done" or "aborted"
    """

    def __init__(self, command=None, stdout_file=None, stderr_file=None):
        self.command = command
        self.pid = None
        self.thread = None
        self.proc = None
        self.evtfunc = None
        self.jsonChange = None
        self.name = "Unnamed" # name of this task
        self.description = ""
        self.stdout_file = stdout_file
        self.stderr_file = stderr_file

        self.lock = threading.Lock()

        # remote variables
        self.remote_path = None
        self.remote_user = None
        self.remote_server = None
        self.remote_id = -1

        # common variables
        self.local = True
        self.state = "waiting"
        self.annotations = "" # custom text
        self.stopEvent = []

        return

    def addStopEvent(self, func):
        """ Add a function that will be called when the execution is finished """
        self.stopEvent.append(func)

    def run(self, command=None, stdout_file=None, stderr_file=None,
            evtfunc=None, local=True, localDirInput=[], localDirOutput=None):
        """
        Transparently manages the execution of a command
        executed in the shell (local or via ssh).

        evtfunc is a function such as: function(task, return_code or None)

        localDirInput = (localInputFolder, remoteInputFolder)
        + localInputFolder folder is an absolute path (no final slash)
        + remoteInputFolder is a relative path (no final slash)

        localDirOutput = (localOutputFolder, remoteOutputFolder)
        + localOutputFolder folder is an absolute path (no final slash)
        + remoteOutputFolder is a relative path (no final slash)
        """
        global CACHE

        if self.state == "running":
            return # Already running

        if not (command is None):
            self.command = command
        else:
            command = self.command

        self.local = local
        if self.local:
            print (" *** EXECUTING local command: " + self.command)
            if not (stdout_file is None):
                self.stdout_file = stdout_file
            if not (stdout_file is None):
                self.stderr_file = stderr_file

            if self.stdout_file is None:
                stdoutf = None
            else:
                stdoutf = open(self.stdout_file, "w")

            if self.stderr_file is None:
                stderrf = None
            else:
                stderrf = open(self.stderr_file, "w")
            # ******************************************************
            #             locked area
            # ******************************************************
            CACHE["local_task_lock"].acquire()
            if self.jsonChange is not None:
                tools.replacePathInJson(self.jsonChange[0],
                                        self.jsonChange[1],
                                        self.jsonChange[2])
            self.proc = subprocess.Popen(self.command, shell=True,
                                         stdout = stdoutf,
                                         stderr = stderrf)
            CACHE["local_task_lock"].release()
            # ******************************************************
            self.pid = self.proc.pid
            self.state = "running"

            if not(evtfunc is None):
                self.evtfunc = evtfunc
                self.thread = threading.Thread(target=self._checkIsRunning)
                self.thread.start()
            return self.pid
        else: # remote execution
            print (" *** EXECUTING remote command: " + str(self.command))
            print(" FOR ID = " + self.name)
            # ******************************************************
            #             locked area
            # ******************************************************
            CACHE["local_task_lock"].acquire()
            if self.jsonChange is not None:
                tools.replacePathInJson(self.jsonChange[0],
                                        self.jsonChange[1],
                                        self.jsonChange[2])

            for dirx in localDirInput:
                print("  SENDING " + dirx[0] + " -> " + dirx[1])
                self.sendFolder(dirx[0], dirx[1])

            # create remote folder for output
            self.localDirOutput = localDirOutput
            if localDirOutput is not None:
                self.executeRemote("mkdir -p '" + self.remote_path +
                                   "/" + localDirOutput[1] + "'")

            # EXECUTE REMOTE COMMAND AND REMEMBER IT
            self.state = "running"
            self.executeRemote(command, background=True,
                               errorControl=True, memorize=True)
            CACHE["local_task_lock"].release()
            # ******************************************************

            print ("WAITING UNTIL LAUNCHED")
            if evtfunc is None:
                self.evtfunc = lambda obj, ok: \
                               self.receiveFolder(self.localDirOutput[0], \
                                                  self.localDirOutput[1]) \
                                                  if ok == True else None
            else:
                self.evtfunc = evtfunc

            self.thread = threading.Thread(target=self._checkIsRunning)
            self.thread.start()
            return None # no remote pid (it's in a file)



    def _checkIsRunning(self):
        """ Private Method: do not call this method,"""
        """ intended to run in an internal thread """
        code = None
        while code is None:
            code = self.checkCode()
            if self.state == "aborted":
                return
            if code is not None:
                if self.local == True:
                    if self.state != "running" and self.state != "aborted":
                        self.evtfunc(self, code)
                    if self.proc is None:
                        return
                    else:
                        time.sleep(0.5)
                    self.evtfunc(self, code)
                else:
                    if self.state == "aborted" or self.state == "done":
                        return
                    self.lock.acquire() # -
                    self.evtfunc(self, code)
                    if code == True:
                        self.freeID() # everything was OK, cleaning
                        self.state = "done"
                    else:
                        self.state = "aborted"
                    self.lock.release() # -
                    return
            elif self.local == False:
                time.sleep(2)



    def checkCode(self): 
        """
        Check if the program has finished and get the ID code
        returned by the executed command when it finishes.

        In the case of remote executions, the function 
        returns True (if success), False (if error only) or None (still running?)

        Return None if the process hasn't finished yet.
        """
        self.lock.acquire() # -
        if self.local == True:
            if self.proc is None:
                self.lock.release() # -
                return None
            else:
                v = self.proc.poll()
                if self.state == "running" and not(v is None):
                    for f in self.stopEvent:
                        f(self, v)
                    #print("PROCESS LOCKED")
                    self.state = "done"
                self.lock.release() # -
                #print("SELF.STATE = " + self.stat)
                return v
        else:
            self.lock.release() # -
            return self.checkRemoteOutput()

    def wait(self):
        """
        Wait until the local command finishes.
        """
        if self.local == False: # remote
            while self.checkRemoteOutput() == None and self.state != "aborted":
                time.sleep(2)
            return
        elif self.proc is None:
            return
        else:
            self.proc.wait()


    def getLog(self, displayErrorInstead=False):
        """ Display stdout or stderr """
        text = ""
        if self.local:
            if not displayErrorInstead:
                f = open(self.stdout_file,"r")
            else:
                f = open(self.stderr_file,"r")
            text = f.read()
            f.close()
        #else:
        # TODO
        return text


    def cancel(self):
        self.lock.acquire()
        self.state = "aborted"
        if self.local:
            if self.proc is None:
                return
            self.proc.terminate()
            self.proc.wait()
        else:
            cmd = "cat \"" + self.remote_path + "/run.pid\""
            pid = self.remoteOutput(cmd)
            try:
                pid = int(pid)
                print("CANCELING REMOTE PROCESS: " + str(pid))
            except:
                print("WARNING: REMOTE PID NOT FOUND: " + pid)
                pid = 0
            if pid > 0:
                self.executeRemote("kill " + str(pid))
        self.lock.release()


    def kill(self):
        self.lock.acquire()
        self.state = "aborted"
        if self.local:
            if self.proc is None:
                return
            #os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.kill()
            self.proc.wait()
        else:
            cmd = "cat \"" + self.remote_path + "/run.pid\""
            pid = self.remoteOutput(cmd)
            try:
                pid = int(pid)
                print("KILLING REMOTE PROCESS: " + str(pid))
            except:
                print("WARNING: REMOTE PID NOT FOUND: " + pid)
                pid = 0
            if pid > 0:
                self.executeRemote("kill -9 " + str(pid))
        self.lock.release()

    def newRemoteID(self):
        """ Get an unique number and set the path and 
        other variables for the given server and create a remote folder for
        the process """
        global CACHE, CONFIG

        if self.remote_id >= 0:
            return # there is already some id

        # Get a new ID
        CACHE["local_task_lock"].acquire()
        prev = int(CONFIG["server/Last remote task (Advanced option)"])
        self.remote_id = prev
        CONFIG["server/Last remote task (Advanced option)"] = prev + 1
        filen = os.path.join(CACHE["program_dir"], "config.json")
        CONFIG.save(filen) # save the new id
        CACHE["local_task_lock"].release()

        # Get a remote PATH
        rpath = CONFIG["server/Remote path"]
        if rpath[-1] == "/": # remove last bar
            rpath = rpath[:-1]
        self.remote_path = rpath + "/" + str(int(self.remote_id))

        # Get the user and the server
        self.remote_user = CONFIG["server/User (optional)"]
        if self.remote_user == "":
            self.remote_user = getpass.getuser()
        self.remote_server = CONFIG["server/Address"]
        # Create the folder
        self.createRemoteFolder()
        self.state = "waiting" # set the state of the process
        return self.remote_id

    def assignRemoteID(self, ID):
        """ Get an unique number and set the path and 
        other variables for the given server and create a remote folder for
        the process """
        global CACHE, CONFIG

        # Copy the given ID
        self.remote_id = ID

        # Get a remote PATH
        rpath = CONFIG["server/Remote path"]
        if rpath[-1] == "/": # remove last bar
            rpath = rpath[:-1]
        self.remote_path = rpath + "/" + str(int(self.remote_id))

        # Get the user and the server
        self.remote_user = CONFIG["server/User (optional)"]
        if self.remote_user == "":
            self.remote_user = getpass.getuser()
        self.remote_server = CONFIG["server/Address"]
        # Create the folder
        self.createRemoteFolder()
        self.state = "waiting" # set the state of the process
        
    def createRemoteFolder(self):
        """
        Create  a remote folder with an unique ID 
        """
        self.executeRemote("mkdir -p '" + self.remote_path + "'")
        return

    def sendFolder(self, localFolder, remoteSubFolder = ""):
        """
        Send a local folder to the server.
        Return True if everything was OK.
        """
        # Windows requirement: http://sshwindows.sourceforge.net/
        global CONFIG,CACHE

        if ( (self.remote_path is None) or
             (self.remote_user is None) or
             (self.remote_server is None) or 
             (self.remote_id < 0)):
            print("Error: None is not expected in path, user, server or id." +
                  " Aborting transfer in sendFonder.")
            return False

        user = self.remote_user
        server = self.remote_server

        # Create remote subfolder to send files if localFolder is a directory
        rpath = self.remote_path + "/" + remoteSubFolder
        if os.path.isdir(localFolder): 
            self.executeRemote("mkdir -p '" + rpath + "'")
            if localFolder != "":
                if localFolder[-1] != os.path.sep:
                    localFolder += os.path.sep
                localFolder = "'" + localFolder + "'"
                localFolder += CACHE["all_files"]
        else:
            print("... warning, is a file, coping the file to " + rpath)

        scppath = CONFIG["SSH/Binaries path"]
        identity = CONFIG["SSH/Certificate file (optional)"]
        if identity != "":
            identity = " -i " + identity
        options = CONFIG["SSH/SSH Options"]

        # create the command
        command = CACHE["prev_exec"]
        command += os.path.join(CONFIG["SSH/Binaries path"], "scp")
        command += CACHE["end_exec"] + " -r "
        command += identity + " " + options + " " + localFolder + " "
        command += user + "@" + server + ":" + "'"
        command += rpath + "'"

        # exec the command
        print("* Transfering: " + command)
        process = subprocess.Popen(command, shell=True)
        process.wait()
        if (process.poll() != 0):
            return False
        else:
            return True


    def receiveFolder(self, localFolder, remoteSubFolder=""):
        """
        Copy the remote folder to a local folder to the server.
        Return True if everything was OK.
        """
        # Windows requirement: http://sshwindows.sourceforge.net/
        global CONFIG

        if ( (self.remote_path is None) or
             (self.remote_user is None) or
             (self.remote_server is None) or
             (self.remote_id < 0)):
            print("Error: None is not expected in path, user, server or id." +
                  " Aborting transfer in sendFonder.")
            return False

        user = self.remote_user
        server = self.remote_server
        rpath = self.remote_path + "/" + remoteSubFolder

        # create the local folder it it doesn't exist
        if not os.path.exists(localFolder):
            os.makedirs(localFolder)

        scppath = CONFIG["SSH/Binaries path"]
        identity = CONFIG["SSH/Certificate file (optional)"]
        if identity != "":
            identity = " -i " + identity
        options = CONFIG["SSH/SSH Options"]
        # create the command
        command = CACHE["prev_exec"]
        command += os.path.join(CONFIG["SSH/Binaries path"], "scp")
        command += CACHE["end_exec"] + " -r "
        command += identity + " " + options + " "
        command += user + "@" + server + ":" + "'"
        command += rpath + "/*' "
        command +=  "'" + localFolder + "'"

        print (" RECEIVING " + rpath + " -> " + localFolder)
        # exec the command
        process = subprocess.Popen(command, shell=True)
        process.wait()
        if (process.poll() != 0):
            return False
        else:
            return True


    def executeRemote(self, command, background=False, errorControl=False, memorize=False):
        """
        Generate a string of text containing the command to be executed in a
        remote server via SSH and NOHUP.
        """
        global CONFIG

        if ( (self.remote_path is None) or
             (self.remote_user is None) or
             (self.remote_server is None) or
             (self.remote_id < 0)):
            print("Error: None is not expected in path, user, server or id." +
                  " Aborting execution in remoteExecutionString.")
            return False

        user = self.remote_user
        server = self.remote_server
        rpath = self.remote_path

        scppath = CONFIG["SSH/Binaries path"]
        identity = CONFIG["SSH/Certificate file (optional)"]
        if identity != "":
            identity = " -i " + identity
        options = CONFIG["SSH/SSH Options"]

        # create the command
        cmd = CACHE["prev_exec"]
        cmd += os.path.join(CONFIG["SSH/Binaries path"], "ssh")
        cmd += CACHE["end_exec"] + " "  + options + " "
        cmd += identity + " "
        cmd += user + "@" + server + " '"
        cmd += os.path.join(CONFIG["server/NOHUP server path"], "nohup")
        cmd += " " + command
        if errorControl:
            cmd +=" && (echo OK > \"" + rpath + "/output.end\")"
            cmd += " || (echo ERR > \"" + rpath + "/output.end\")"
        if background:
            cmd += " & echo $! > \"" + rpath + "/run.pid\"' &"
        else:
            cmd += " '"

        # *-------------------------------*
        # Execute the command:
        print("   Remote COMMAND: " + cmd)
        process = subprocess.Popen(cmd, shell=True)
        if (not background):
            process.wait()
        #self.state = "running" # this state only must change in method run
        return process

    def freeID(self):
        """ Remove the remote temporal directory and nullify the id"""
        if self.remote_id < 0:
            return
        p = self.executeRemote("rm -r '" + self.remote_path + "'")
        self.remote_id = -1

    def checkRemoteOutput(self):
        """
        Return True if a remote command was executed succefully, False otherwise.
        If the remote command did not finished, return None
        """
        global CONFIG

        self.lock.acquire()
        # first check if the process was aborted
        if self.state == "aborted":
            self.lock.release()
            return False

        # create the command
        cmd = "cat " + self.remote_path + "/output.end 2> /dev/null"
        # *-------------------------------*
        output = self.remoteOutput(cmd)
        #print("CAT _ OUTPUT = " + str(output.strip()))
        if output.strip() == b"OK":
            #print("<OK>")
            self.lock.release()
            return True
        elif output.strip() == b"ERR":
            print("<ERR> " + self.name)
            self.lock.release()
            return False
        self.lock.release()
        return None

    def remoteOutput(self, command):
        """
        Return the output of a remote command as a string.
        """
        global CONFIG

        if ( (self.remote_path is None) or
             (self.remote_user is None) or
             (self.remote_server is None) or
             (self.remote_id is None)):
            print("Error: None is not expected in path, user, server or id." +
                  " Aborting execution in checkRemoteOutput.")
            return False

        user = self.remote_user
        server = self.remote_server
        rpath = self.remote_path

        scppath = CONFIG["SSH/Binaries path"]
        identity = CONFIG["SSH/Certificate file (optional)"]
        if identity != "":
            identity = " -i " + identity
        options = CONFIG["SSH/SSH Options"]

        # create the command
        cmd = CACHE["prev_exec"]
        cmd += os.path.join(CONFIG["SSH/Binaries path"], "ssh")
        cmd += CACHE["end_exec"] + " "  + options + " "
        cmd += identity + " "
        cmd += user + "@" + server + " '"
        cmd += os.path.join(CONFIG["server/NOHUP server path"], "nohup")
        cmd += " " + command + "'"


        # *-------------------------------*
        # Execute the command:
        print("   COMMAND (chkout) " + cmd)

        try:
            output = subprocess.check_output(cmd, shell=True)
        except:
            return ""
        return output

    def save(self):
        """ Return some structure suitable to be saved,
            local tasks are stored as done or aborted """
        data = {}
        data["command"] = self.command
        data["pid"] = self.pid
        data["jsonChange"] = self.jsonChange
        data["name"] = self.name
        data["description"] = self.description
        data["remote_path"] = self.remote_path
        data["remote_user"] = self.remote_user
        data["remote_server"] = self.remote_server
        data["remote_id"] = self.remote_id
        data["local"] = self.local
        if self.local and self.state != "done":
            data["state"] == "aborted"
        else:
            data["state"] = self.state
        data["annotations"] = self.annotations

        return

    def load(self, data):
        """
        Restore data, data must be in a suitable structure
        (such as used in save), only remote tasks recover the
        default evtfunc.
        """
        self.command = data["command"]
        self.pid = data["pid"]
        self.jsonChange = data["jsonChange"]
        self.name = data["name"]
        self.description = data["description"]
        self.remote_path = data["remote_path"]
        self.remote_user = data["remote_user"]
        self.remote_server = data["remote_server"]
        self.remote_id = data["remote_id"]
        self.local = data["local"]
        if self.local and self.state != "done":
            data["state"] == "aborted"
        else:
            data["state"] = self.state
        data["annotations"] = self.annotations

        # TODO
        if self.local == False: 
            self.evtfunc = lambda obj, ok: \
                           self.receiveFolder(self.localDirOutput[0], \
                                              self.localDirOutput[1]) \
                                              if ok == True else None
            self.thread = threading.Thread(target=self._checkIsRunning)
            self.thread.start()

        return
