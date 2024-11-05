import os
import os.path
import resource
import subprocess
import time
# import uuid
from threading import Timer
from typing import List, Union


def limit_memory(maxsize: int, hardmax: int = resource.RLIM_INFINITY) -> None:
    """Limit the memory usage for the process."""
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hardmax))


def terminate(process: subprocess.Popen, is_timeout: List[bool]) -> None:
    """Terminate the process on timeout."""
    if process.poll() is None:
        try:
            process.terminate()
            is_timeout[0] = True
        except Exception as e:
            print("Error interrupting process:", e)


def isexec(fpath: Union[str, None]) -> bool:
    """Check if the file path is an executable."""
    return fpath is not None and os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def run_cmd(cmd_tool: List, timeout=300):
    """Run a command within a time limit"""
    out_tool = None
    try:
        time_start = time.time()
        ptool = subprocess.Popen(cmd_tool, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # start_time = time.time()
        is_timeout = [False]
        timer = Timer(timeout, terminate, args=[ptool, is_timeout])
        timer.start()

        out_tool = ptool.stdout.readlines()
        out_tool = ' '.join([str(element.decode('UTF-8')) for element in out_tool])
        ptool.stdout.close()

        timer.cancel()
        return time.time() - time_start
    except Exception as ex:
        print("Exception occurred:", ex)
        return -1


def which(program: Union[str, List[str]]) -> Union[str, None]:
    """Locate a program file on the system path."""
    choices = [program] if isinstance(program, str) else program

    for p in choices:
        fpath, _ = os.path.split(p)
        if fpath:
            if isexec(p):
                return p
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, p)
                if isexec(exe_file):
                    return exe_file
    return None
