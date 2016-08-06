"""
    Guild Wars 2 multiaccount launcher and multiboxer.
    Requires administrator mode.
    Multiboxing works by closing the "AN-Mutex-Window-Guild Wars 2" handle of
        each game instance and making Local.dat a symbolic link to the .dat
        file connected to the intended account.
    Script stores all variables using JSON format in a file named data.json
        which is located in the same directory as the script.

    Variables:
    - handle: path to handle.exe file
        https://technet.microsoft.com/en-us/sysinternals/handle.aspx
    - localPath: the path to the directory where the Local.dat file is located
        default: "%AppData%\Guild Wars 2"
    - exePath: path to the Guild Wars 2 executable file
        default: "%ProgramFiles%\Guild Wars 2\Gw2-64.exe"
    - params: Guild Wars 2 launch parameters for single instance
        https://wiki.guildwars2.com/wiki/Command_line_arguments
    - multiparams: Guild Wars 2 launch parameters for multibox launch
        "-shareArchive" is added automatically
"""

import os
import re
import subprocess
import shutil
import time
import json
from glob import glob
from sys import exit

# This file's location
__location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))


def main():
    """ Asks user to pick option """
    # Get variables from data.json or create one if data.json does not exist
    getJSON()

    if "-shareArchive" not in multiparams:
        multiparams.append("-shareArchive")
    # Get all .dat files in localPath
    users = glob(os.path.join(localPath, "*.dat"))
    # Remove Local.dat from users array
    try:
        users.remove(datLocal)
    except ValueError:
        pass

    print("\nHere are your options:")
    print("1) Exit")
    print("2) Edit program variables or add new account")
    print("3) Multibox")
    print("4) Current account")

    # List users array
    for i, name in enumerate(users):
        print("%d) %s" % (i + 5, os.path.basename(name[:-4])))

    # ensure valid input
    choice = 0
    while not (0 < choice <= (len(users) + 4)):
        try:
            choice = int(input("Please select an option between 1 and %d: "
                               % (len(users) + 4)).strip())
        except ValueError:
            choice = 0

    if choice == 1:
        exit()
    elif choice == 2:
        changeData()
    elif choice == 3:
        multibox(users)
    elif choice == 4:
        startSingle()
    else:
        startSingle(users[choice - 5])


def newUser():
    """ Create new Guild Wars 2 user"""
    name = input("What is the name of the new account? ") + ".dat"
    try:
        params.remove("-autologin")
    except ValueError:
        pass

    print("Please login with the new account for it to be saved")
    datFile = os.path.join(localPath, name)
    # Create empty file
    open(datFile, "a").close()
    startSingle(datFile)


def startSingle(datFile=None, multi=False):
    """ Starts a single game instance """
    # Create symbolic link from datFile to datLocal
    if datFile:
        try:
            os.remove(datLocal)
        except FileNotFoundError:
            pass
        os.symlink(datFile, datLocal)

    if multi:
        command = [exePath] + multiparams
    else:
        command = [exePath] + params
    # Launch game instance with correct parameters
    subprocess.Popen(command)


def multibox(users):
    """ Multibox main """
    updateGame()

    print("\nHere are your options:")
    print("1) Return to main menu")
    for i, name in enumerate(users):
        print("%d) %s" % (i + 2, os.path.basename(name[:-4])))

    # ensure valid input
    choices = list()
    while not (choices and min(choices) > 1 and
               max(choices) <= (len(users) + 1) and
               len(set(choices)) == len(choices)):
            # Get user input as string
        choices = input(
            "Select which accounts to open by enetering their respective" +
            " numbers seperated by a space (Ex. \"2 3 7\"). " +
            "Or select 1 to exit. "
        ).strip()

        # Return to main menu if 1 is selected
        if choices == "1":
            gotoMain()

        # Turn user input into integer array
        try:
            choices = list(map(lambda x: int(x), choices.split()))
        except ValueError:
            choices = list()

    # map .dat files location over their index
    choices = list(map(lambda x: users[x - 2], choices))

    # get the instances started
    for choice in choices:
        startMulti(choice)


def startMulti(datFile):
    """ Handles creation of a multibox instance """
    startSingle(datFile, True)
    # Wait for instance to start
    time.sleep(5)
    shutMutex()


def shutMutex():
    """ Close the "AN-Mutex-Window-Guild Wars 2" mutant handle """
    command = [handle, "-a \"AN-Mutex-Window-Guild Wars 2\""]

    # get the raw response of the handle command
    handle_response = str(subprocess.check_output(" ".join(command)))

    # get the pid code
    pid = re.compile("pid: \d+").search(handle_response).span()
    pid = handle_response[pid[0] + 5:pid[1] + 1]

    # get the hex value of the mutant
    val = re.compile("\w+: \\\\").search(handle_response).span()
    val = handle_response[val[0]:val[1] - 3]

    # shut the Mutex
    command = [handle, "-c %s" % val, "-p %s" % pid, "-y"]
    subprocess.call(" ".join(command))


def updateGame():
    """ Update game client """
    command = [exePath, "-image"]
    subprocess.call(command)


def getJSON():
    """ Gets data from data.json and create's one if all data is not found """
    global handle, localPath, exePath, params, multiparams, datLocal
    try:
        with open(os.path.join(__location__, "data.json")) as reader:
            data = json.load(reader)
            handle = data["handle"]
            localPath = data["localPath"]
            exePath = data["exePath"]
            params = data.get("params", list())
            multiparams = data.get("multiparams", list())
    except (FileNotFoundError, KeyError):
        createData()

    # Define Local.dat path
    datLocal = os.path.join(localPath, "Local.dat")


def createData():
    """ Creates a new data.json file in file's directory """
    global handle, localPath, exePath, params, multiparams
    data = dict()
    handle = input("Path to handle.exe: ")
    localPath = input("Path to Local.dat folder " +
                      "(default is %s, press enter to use default)" %
                      os.path.join(os.getenv("APPDATA"), "Guild Wars 2"))
    if localPath == "":
        localPath = os.path.join(os.getenv("APPDATA"), "Guild Wars 2")
    exePath = input("Path to Gw2.exe (64-bit or 32-bit) " +
                    "(default is %s, press enter to use default)" %
                    os.path.join(os.getenv("PROGRAMFILES"), "Guild Wars 2",
                                 "Gw2-64.exe"))
    if exePath == "":
        exePath = os.path.join(os.getenv("PROGRAMFILES"), "Guild Wars 2",
                               "Gw2-64.exe")
    params = input("Add Guild Wars 2 parameters" +
                   "(ex. \"-autologin -maploadinfo -bmp\"): ").split()
    multiparams = input("Add Guild Wars 2 parameters for multiboxing " +
                        "(ex. \"-autologin -nosound -bmp\"): ").split()

    data["handle"] = handle
    data["localPath"] = localPath
    data["exePath"] = exePath
    data["params"] = params
    data["multiparams"] = multiparams
    with open(os.path.join(__location__, "data.json"), "w") as writer:
        writer.write(json.dumps(data))


def changeData():
    try:
        data = json.load(open(os.path.join(__location__, "data.json")))
    except FileNotFoundError:
        print("Can't find data.json file. Creating new one")
        createData()
        return

    print("\nHere are your options:")
    print("1) Return to main menu")
    print("2) Change handle.exe location")
    print("3) Change Local.dat directory location")
    print("4) Change Gw2.exe location")
    print("5) edit parameters")
    print("6) edit multiparmeters")
    print("7) add a new GW2 account")

    choice = 0

    while not (0 < choice < 8):
        try:
            choice = int(input("Pick a number between 1 and 7: "))
        except ValueError:
            choice = 0

    if choice == 1:
        gotoMain()
    elif choice == 2:
        data["handle"] = input()
    elif choice == 3:
        data["localPath"] = input()
    elif choice == 4:
        data["exePath"] = input()
    elif choice == 5:
        data["params"] = input().split()
    elif choice == 6:
        data["multiparams"] = input().split()
    elif choice == 7:
        newUser()

    with open(os.path.join(__location__, "data.json"), "w") as writer:
        writer.write(json.dumps(data))
    gotoMain()


def gotoMain():
    """ Call main then exit script """
    main()
    exit()

if __name__ == "__main__":
    main()
