import subprocess
import os

"""
ProcessWrapper is a utility class to manage the execution of a process
It stores the PID of the process in a specified file and provides methods to run the process

TODO: writing to a file is stupid!
lets try RAM instead to store the PID
and maybe convert from a subprocess to something nicer
"""
class ProcessWrapper:
    def __init__(self, pid_file: os.path, process: lambda: subprocess.Popen):
        self.pid_file: os.path = pid_file
        self.process = process
        self._proc = None

    def run(self):
        self._proc = self.process()
        self._write(str(self._proc.pid))
        self._proc.wait()
        self._proc = None
        self._write()

    def runSkipWrite(self):
        if not self._proc:
            self._proc = self.process()
        return self._proc

    def _write(self, content: str = ""):
        if not self.pid_file:
            raise ValueError("PID file path is not set.")
        with open(self.pid_file, "w") as f:
            f.write(content)
