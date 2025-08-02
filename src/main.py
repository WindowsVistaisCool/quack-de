from lib.DevChecks import isDev
from lib.ProcessWrapper import ProcessWrapper
from subprocess import Popen

if __name__ == "__main__":
    wrapper = ProcessWrapper("./window.pid", lambda: Popen(["python3", "./App.py"]))

    if isDev():
        wrapper.runSkipWrite()
    else:
        wrapper.run()
