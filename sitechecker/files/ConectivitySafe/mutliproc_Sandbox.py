import sys
import os
import subprocess
import time

def run_wvdial():
    wvdial = subprocess.Popen(['sudo', 'wvdial', 'infraestructuras'],
                     stdout=subprocess.PIPE,
                     universal_newlines=True)

def spawnDaemon(func):
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # parent process, return and keep running
            return
    except OSError:
        print("fork error")
        sys.exit(1)

    os.setsid()

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError:
        print("fork error")
        sys.exit(1)

    # do stuff
    func()

    # all done
    os._exit(os.EX_OK)



if __name__ == "__main__":
    spawnDaemon(run_wvdial_Proc)
    time.sleep(10)
