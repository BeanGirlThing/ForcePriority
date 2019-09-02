import os
import threading
from time import sleep

import prettytable
import psutil


class main:

    helpDialogue = """
=== Help ===

ForcePriority is a utility that forces a process to have a certain priority.
This is useful because some processes automatically change their priority to a specified point.
For example Discord will set its priority back to normal every five minutes if changed.

Tables:

"Process list" - This table shows all running processes on your computer.
This program refers to programs based on their PID or Process IDentification. 
To specify a process to this program, look down the list for its name and then note down the PID found next to the name.
This program will request the PID of the program you wish to force the priority of.

"Targets" - This table shows the list of processes currently being targeted by this program.
You can remove a program from this list by using the "remove" command and supplying the PID of the program you wish to remove.

Priority ID reference:

Priority Level ID: 	Priority Level Name:

256 	            Realtime
128 	            High
32768 	            Above normal
32 	                Normal
16384 	            Below normal
64 	                Low

Command list:
add - Allows you to add a process to the targeted processes list.
remove - Allows you to remove a process from the targeted process list.
help - Display this dialogue.
reload - Reloads process lists. 
exit - Exits the process.

============
    """

    clearToPrint = 0
    #This list holds the process ID and wanted priority.
    processSpec = []

    def checkLoop(self):
        """
        This function is threaded to check the system priorities of the specified
        applications every second, if they have reset it will put them back to what the user wants.
        """
        # Main loop
        while True:

            # While there are no specified processes hold in a loop to conserve system resources.
            while self.processSpec == []:
                # Wait for one second to conserve system resources
                sleep(1)

            for i in range(0,len(self.processSpec)):
                try:
                    procPri = self.processSpec[i][0].nice()
                    if procPri != self.processSpec[i][1]:
                        if self.clearToPrint == 1:
                            print(f"Process {self.processSpec[i][1]} has changed its priority to {procPri}")
                        self.processSpec[i][0].nice(self.processSpec[i][1])
                except psutil.NoSuchProcess:
                    if self.clearToPrint == 1:
                        print(f"Process {self.processSpec[i][1]} no-longer exists, removing from targets.")
                    self.processSpec.pop(i)


            sleep(1)



    def userInterface(self):
        """
        This will be the function the user will interface with, this will contain a table of processes
        and selected processes.
        """
        while True:
            self.mainTable.clear_rows()
            proclist = []
            for proc in psutil.process_iter():
                try:
                    proclist.append(proc)
                except psutil.NoSuchProcess:
                    pass

            for process in proclist:
                try:
                    dictpro = process.as_dict(["name","pid","username","status"])
                except psutil.NoSuchProcess:
                    print("Process no-longer exists, skipping")
                    continue
                self.mainTable.add_row([dictpro["name"],dictpro["pid"],dictpro["username"],dictpro["status"]])

            if self.processSpec != []:
                self.specifyTable.clear_rows()
                for i in range(0,len(self.processSpec)):
                    try:
                        dictpro = self.processSpec[i][0].as_dict(["name","pid","username"])
                    except psutil.NoSuchProcess:
                        print("Process no-longer exists, skipping and removing from target list")
                        self.processSpec.pop(i)
                        continue
                    self.specifyTable.add_row([dictpro["name"],dictpro["pid"],dictpro["username"],self.processSpec[i][1]])
            else:
                self.specifyTable.clear_rows()

            while True:
                print("Process list:")
                print(self.mainTable)
                print("Targets:")
                print(self.specifyTable)
                print("Type 'help' for more information.")
                userIn = input(">").strip(" ")

                if userIn == "":
                    continue

                if userIn.upper() == "EXIT":
                    print("Goodbye")
                    sleep(1)
                    os._exit(0)


                if userIn.upper() == "REMOVE":
                    while True:
                        try:
                            targetProcess = int(input("PID of the process you wish to remove from the targeted list: "))
                            break
                        except ValueError:
                            print("PID must be int (Number, please ensure no symbols or letters were used).")
                            continue
                    a = 0
                    for i in range(0,len(self.processSpec)):
                        tempProc = self.processSpec[i][0].as_dict(["pid"])
                        if targetProcess == tempProc["pid"]:
                            self.processSpec.pop(i)
                            a = 1
                            break

                    if a == 0:
                        print("No target process was found with that PID, therefore nothing was changed.")
                        continue
                    else:
                        print("Done, reloading processes.")
                        break

                if userIn.upper() == "RELOAD":
                    print("Reloading processes")
                    break

                if userIn.upper() == "HELP":
                    print(self.helpDialogue)
                    input("Press enter to continue.")

                elif userIn.upper() == "ADD":
                    while True:
                        try:
                            targetProcess = int(input("PID of the process you wish to target: "))
                            break
                        except ValueError:
                            print("PID must be int (Number, please ensure no symbols or letters were used).")
                            continue
                    while True:
                        print("Please select a priority.\n[0] Realtime\n[1] High\n[2] Above normal\n[3] Normal\n[4] Below normal\n[5] Idle")
                        try:
                            priority = int(input(">"))
                            break
                        except ValueError:
                            print("Selection must be int (Number, please ensure no symbols or letters were used).")
                            continue
                    i = 0
                    for process in proclist:
                        pidOfTarget = process.as_dict(["pid"])
                        if targetProcess == int(pidOfTarget["pid"]):
                            i = 1
                            if priority == 0:
                                self.processSpec.append([process, psutil.REALTIME_PRIORITY_CLASS])
                            if priority == 1:
                                self.processSpec.append([process, psutil.HIGH_PRIORITY_CLASS])
                            if priority == 2:
                                self.processSpec.append([process, psutil.ABOVE_NORMAL_PRIORITY_CLASS])
                            if priority == 3:
                                self.processSpec.append([process, psutil.NORMAL_PRIORITY_CLASS])
                            if priority == 4:
                                self.processSpec.append([process, psutil.BELOW_NORMAL_PRIORITY_CLASS])
                            if priority == 5:
                                self.processSpec.append([process, psutil.IDLE_PRIORITY_CLASS])

                    if i == 0:
                        print("PID could not be identified and tagged to a process.")

                    print("Done, reloading processes.")
                    break

                else:
                    print("Command not recognised. Use the command 'help' to show a list of commands.")
                    input("Press enter to continue.")
                    continue

    def __init__(self):
        print("Now loading")
        self.mainTable = prettytable.PrettyTable(("Name","PID","Username","Status"))
        self.specifyTable = prettytable.PrettyTable(("Name","PID","Username","Requested Priority"))
        ui = threading.Thread(target=self.userInterface)
        check = threading.Thread(target=self.checkLoop, daemon=True)
        ui.start()
        check.start()
        ui.join()
        check.join()
        print("Process ended successfully")

if __name__ == "__main__":
    main()