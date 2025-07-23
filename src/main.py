from lib.PidWrapper import PidWrapper
from subprocess import Popen
from os import path

def isDev():
    return path.exists("../dev")

if __name__ == '__main__':
    wrapper = PidWrapper("./window.pid", lambda: Popen(["python3", "./window.py"]))

    if isDev():
        wrapper.runSkipWrite()
    else:
        wrapper.run()
