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
import datetime
import os.path
import threading 


class TaskData:
    """ Default  Constructor """
    def __init__(self, task, data, date, local = True,
                 localDirInput = [], localDirOutput = None):
        self.task = task
        self.data = data
        self.date = date
        self.local = local
        self.localDirInput = localDirInput
        self.localDirOutput = localDirOutput

    def save(self):
        """ Return some structure suitable to be saved """
        data = {}
        data["task"] = self.task.save()
        data["date"] = self.date
        data["local"] = self.local
        data["localDirInput"] = self.localDirInput
        data["localDirOutput"] = self.localDirOutput
        return data

    def load(self, data):
        """
        Restore data, data must be in a suitable structure
        (such as used in save)
        """
        self.task.load(data["task"])
        self.date = data["date"]
        self.local = data["local"]
        self.localDirInput = data["localDirInput"]
        self.localDirOutput = data["localDirOutput"]
        return

class TaskManager(threading.Thread):
    """ Class that allow to launch task in a dependence chain """

    def __init__(self, sleep=0.3):
        """ Initialize this class """
        threading.Thread.__init__(self)
        self._tasks = []
        self.all_tasks_done = False
        self._dateFormat = "%I:%M:%S%p on %B %d, %Y"
        self._sleep = sleep
        self._lock = threading.Lock()
        return

    def addTask(self, task, local=True,
                localDirInput = [], localDirOutput = None):
        """ Add an independent task """
        timestamp = datetime.datetime.now().strftime(self._dateFormat)
        self.all_tasks_done = False
        tsk = TaskData(task, ("nil", None), timestamp,
                       local, localDirInput, localDirOutput)
        self._tasks.append(tsk)
        self.exec_()
        return


    def addTaskDependOnFiles(self, task, dependency_files, local=True,
                             localDirInput = [], localDirOutput = None):
        """ Add a task that will be lauch when the dependecy_files exist """
        timestamp = datetime.datetime.now().strftime(self._dateFormat)
        self.all_tasks_done = False
        tsk = TaskData(task, ("files", dependency_files), timestamp,
                       local, localDirInput, localDirOutput)
        self._tasks.append(tsk)
        self.exec_()
        return

    def addTaskDependOnFunction(self, task, f, local=True,
                 localDirInput = [], localDirOutput = None):
        """ Add a task that will be lauch when the function f returns true, """
        """ if f returns None it is considered as abortion """
        timestamp = datetime.datetime.now().strftime(self._dateFormat)
        self.all_tasks_done = False
        tsk = TaskData(task, ("function", f), timestamp,
                       local, localDirInput, localDirOutput)
        self._tasks.append(tsk)
        self.exec_()
        return

    def addTaskDependOnTask(self, task, previous_task, local=True,
                            localDirInput = [], localDirOutput = None):
        """ Add a task that will be lauch when the dependecy_files exist """
        timestamp = datetime.datetime.now().strftime(self._dateFormat)
        self.all_tasks_done = False
        tsk = TaskData(task, ("task", previous_task), timestamp,
                       local, localDirInput, localDirOutput)
        self._tasks.append(tsk)
        self.exec_()
        return

    def _update(self):
        """ Update the manager, to lauch tasks """
        """ if neccessary, and to check files """
        self._lock.acquire()
        index = 0
        tasks_done = True
        for t in self._tasks:
            if t is None: # skip nil values
                continue

            task = t.task
            if task.state != "done" and task.state != "aborted":
                tasks_done = False
                if t.local:
                    task.checkCode()
            #print(" TASK[\"" + str(task.name) + "\"] = ", task.state)
            if task.state != "waiting":
                continue

            depend = t.data[0]
            if depend == "nil":
                print (" ___ TASK MANAGER: nil task -> " +
                       str(t.localDirInput) + " / " +
                       str(t.localDirOutput))
                print ("        " + t.task.name)
                task.run(local=t.local,
                         localDirInput = t.localDirInput,
                         localDirOutput = t.localDirOutput)
            elif depend == "task":
                prev_task = t.data[1]
                if prev_task.state == "done":
                    print (" ___ TASK MANAGER: waked task -> " +
                           str(t.localDirInput) + " / " + str(t.localDirOutput))
                    print ("        " + t.task.name)
                    task.run(local=t.local,
                             localDirInput = t.localDirInput,
                             localDirOutput = t.localDirOutput)
                elif prev_task.state == "aborted": # task aborted
                    self._tasks[index] = None # set to garbage
            elif depend == "files":
                fileList = t.data[1]
                ok = True
                # check if some of the files is missing
                for f in fileList:
                    if (not os.path.exists(f)):
                        ok = False
                        break

                if ok:
                    print (" ___ TASK MANAGER: depending on files -> " + str(t.data[1]))
                    print ("        " + t.task.name)
                    task.run(local=t.local,
                             localDirInput = t.localDirInput,
                             localDirOutput = t.localDirOutput)
            else: # depend == "function"
                f = t.data[1]
                if f() == True:
                    print (" ___ TASK MANAGER: depending on functions -> " + str(t.localDirInput) + " / " + str(t.localDirOutput))
                    print ("        " + t.task.name)
                    task.run(local=t.local,
                             localDirInput = t.localDirInput,
                             localDirOutput = t.localDirOutput)
                elif f() == None: # task aborted
                    self._tasks[index] = None # set to garbage

            index += 1

        # remove garbarge
        self._tasks = [x for x in self._tasks if x is not None and x.task.state != "done"]
        # update the flag
        self.all_tasks_done = tasks_done
        #print("TASKS_DONE = ", tasks_done)
        self._lock.release()
        self.exec_()
        return

    def tasks(self):
        return self._tasks

    def exec_(self):
        if not self.all_tasks_done:
            self._timer = threading.Timer(self._sleep, self._update, [])
            self._timer.start()


    def save (self):
        global PROJECT
        """ Save remote tasks in the project """
        data = {}
        data["_sleep"] = self._sleep
        data["_tasks"] = []
        for t in self._tasks:
            data["_tasks"].append(t.save())
        PROJECT["task_manager"] = data
        return

    def load(self):
        global PROJECT
        """ Restore remote task from the project """
        data = PROJECT["task_manager"]
        self._sleep = data["_sleep"]
        self._tasks = []
        for d in data["_tasks"]:
            t = TaskData(None, None, None)
            t.load(d)
            self._tasks.append(t)
        return
