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

global handle, localPath, exePath, params, multiparams, datLocal


def main():
    """ Asks user to pick option """
    # Check for JSON file and create one if there isn't
    getJSON()
    # Get all dat files in localPath
    users = glob(os.path.join(localPath, "*.dat"))
    # Remove Local.dat from the array
    users = list(filter(lambda x: os.path.basename(x) != "Local.dat", users))

    print("Here are your options:")
    print("1) Create/change program variables")
    print("2) Multibox")
    print("3) Current account")

    for i, name in enumerate(users):
        print("%d) %s" % (i + 4, os.path.basename(name[:-4])))

    # ensure valid input
    choice = 0
    while not (0 < choice <= (len(users) + 3)):
        try:
            choice = int(input("Please select an option between 1 and %d: "
                               % (len(users) + 3)))
        except ValueError:
            choice = 0

    if choice == 1:
        changeData()
    if choice == 2:
        multibox(users)
    elif choice == 3:
        startSingle()
    else:
        startSingle(users[choice - 4])


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
    subprocess.Popen(command)


def multibox(users):
    """ Multibox main """
    updateGame()

    print("\nHere are your options:")
    for i, name in enumerate(users):
        print("%d) %s" % (i + 1, os.path.basename(name[:-4])))

    # ensure valid input
    choices = [0]
    while not (choices and min(choices) > 0 and max(choices) <= len(users) and
               len(set(choices)) == len(choices)):
        try:
            # Get user input as string and turn it into an integer array
            choices = list(map(lambda x: int(x), input("Select which " +
                                                       "accounts to open by " +
                                                       "entering the numbers" +
                                                       " seperated by a " +
                                                       "space(Ex. 1 2 3). "
                                                       ).split()))
        except ValueError:
            choices = [0]

    # map dat file location over index
    choices = list(map(lambda x: users[x - 1], choices))

    # get the instances started
    for choice in choices:
        startMulti(choice)


def startMulti(datFile):
    """ handles creation of a multibox instance """
    gwcomm = [exePath] + multiparams
    startSingle(datFile, True)
    time.sleep(5)
    shutMutex()


def shutMutex():
    """ shuts the mutant aspect """
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

    # Define the Local.dat location
    datLocal = os.path.join(localPath, "Local.dat")


def createData():
    global handle, localPath, exePath, params, multiparams
    data = dict()
    handle = input("Path to handle.exe: ")
    localPath = input("Path to Local.dat folder " +
                      "(default is %s, leave empty to use that)" %
                      os.path.join(os.getenv("APPDATA"), "Guild Wars 2"))
    if localPath == "":
        localPath = os.path.join(os.getenv("APPDATA"), "Guild Wars 2")
    exePath = input("Path to Gw2.exe (64-bit or 32-bit)")
    params = input("Add Guild Wars 2 parameters" +
                   "(ex. \"-autologin -maploadinfo -bmp\"): ").split()
    multiparams = input("Add Guild Wars 2 parameters for multiboxing " +
                        "(ex. \"-autologin -nosound -bmp\"): ").split()

    data["handle"] = handle
    data["localPath"] = localPath
    data["exePath"] = exePath
    data["params"] = params
    data["multiparams"] = multiparams + ["-shareArchive"]
    with open(os.path.join(__location__, "data.json"), "w") as writer:
        writer.write(json.dumps(data))


def changeData():
    data = json.load(open(os.path.join(__location__, "data.json")))

    print("1) Change handle.exe location")
    print("2) Change Local.dat directory location")
    print("3) Change Gw2.exe location")
    print("4) edit parameters")
    print("5) edit multiparmeters")
    print("6) add a new GW2 account")

    choice = 0

    while not (0 < choice < 7):
        try:
            choice = int(input("Pick a number between 1 and 6 "))
        except ValueError:
            choice = 0

    if choice == 1:
        data["handle"] = input()
    if choice == 2:
        data["localPath"] = input()
    if choice == 3:
        data["exePath"] = input()
    if choice == 4:
        data["params"] = input().split()
    if choice == 5:
        data["multiparams"] = input().split() + ["-shareArchive"]
    if choice == 6:
        newUser()

    with open(os.path.join(__location__, "data.json"), "w") as writer:
        writer.write(json.dumps(data))
    exit()

if __name__ == "__main__":
    main()
