import subprocess
from multiprocessing import Process
import serial
import socket
import os
import time
import sys
import logging
import logging.handlers
from reset_usb_device import reset_USB_Device
from atmega_signal import flanco

#check if log dir and file is created:
dir_path = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(dir_path,'logs')
# create log folder if it doesnt exist
if os.path.isdir(log_dir) == False:
    os.mkdir(log_dir)

log = logging.getLogger('ConnSafe')
log.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
size_handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, 'ConnSafe.log'),
                              mode='a',
                              maxBytes=1000000,
                              backupCount=5,
                              encoding='utf-8',
                              delay=0)

size_handler.setLevel(logging.DEBUG)
size_handler.setFormatter(log_format)
log.addHandler(size_handler)

def restart_modem(port):
        try:
            modem_serial = serial.Serial(port='/dev/ttyUSB{}'.format(port),
                                         baudrate=9600,
                                         timeout=5)
            atcommand = 'AT+CPOF'
            command = atcommand + '\r'
            modem_serial.write(command.encode())
            modem_response = modem_serial.read(200)
            print("port {0} reponse is: {1}".format(port, modem_response))
            if "OK" in modem_response.decode("utf-8"):
                log.info('Modem restarted in port {}'.format(port))
                return True
        except:
            log.error('Couldnt restart modem in port {}'.format(port))

def modemPorts():
    """
    :return: returns a list with the ports available
    """
    ports = []
    for port in range(10):
        try:
            modem_serial = serial.Serial(port='/dev/ttyUSB{}'.format(port),
                                         baudrate=9600,
                                         timeout=5)
            atcommand = 'AT'
            command = atcommand + '\r'
            modem_serial.write(command.encode())
            modem_response = modem_serial.read(200)
            print("port {0} reponse is: {1}".format(port, modem_response))
            if "OK" in modem_response.decode("utf-8"):
                ports.append(port)
        except Exception as e:
            print(e)
            print("port {} doesnt answer".format(port))
    return ports

def run_wvdial():
    log.info("Running wvdial")
    wvdial = subprocess.Popen(['sudo', 'wvdial', 'infraestructuras'],
                              stdout=subprocess.PIPE,
                              universal_newlines=True)

def findWvdial():
    wvdialexists = writeShell('ps -aux | grep wvdial', ['wvdial infraestructuras', 'pppd'], check=True)
    print(wvdialexists)
    if wvdialexists == False:
        log.info('Wvdial doesnt found')
    else:
        log.info("Wvdial was found")
    return wvdialexists

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

def writeShell(command, wordsTrue = None, wordsFalse = None, check = False):
    """
    :param words: words to look for in output
    :param command: command to write in shell
    :return: True if found
    """
    log.info("Writting in shell: {}".format(command))
    ps = subprocess.Popen(command,
                          shell=True,
                          stdout= subprocess.PIPE)
    #TODO add to get output or timeout for avoid wait(in that case false)
    if check == True:
        for line in iter(ps.stdout.readline, ''):
            print(line)
            line = line.decode('UTF-8')  # bytes to str

            if wordsTrue:
                for sentence in wordsTrue:
                    if sentence in line:
                        log.info("'{}' found in the ps-aux output , process True".format(sentence))
                        print(line)
                        return True
                    else:
                        return False
            if wordsFalse:
                for sentence in wordsFalse:
                    if sentence in line:
                        log.info("'{}' found in the ps-aux output, process False".format(sentence))
                        print(line)
                        return False
                    else:
                        return True

            if line == '':
                break

def addroute():
    log.info('Adding route ppp0')
    return writeShell('sudo route add default ppp0', wordsFalse =['No such device'], check = True)

def delroute():
    log.info('Deleting route ppp0')
    return writeShell('sudo route del default ppp0', wordsFalse = ['No such device'], check=True)

def kill(app):
    log.info('Killing {}'.format(app))
    writeShell('sudo pkill -f {}'.format(app))

def safeReboot():
    log.info('Applying reset to micro for safe reboot')
    flanco()
    log.info('Rebooting system')
    writeShell('sudo reboot now')

def linkStatus():
    #TODO the socket seems to hangs on disconnect, have to be changed
    def alive_status(ip, port):

            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.settimeout(5)
            try:
                _socket.connect((ip, port))
                return  True
            except socket.timeout:
                log.info("Socket timeout")
                return False
            except:
                log.info("error desconocido")
                return False


    SERVER_LIST = {'argos': {'ip': '10.118.212.79',
                             'port': 80},
                   'src': {'ip': '10.118.214.115',
                           'port': 8080},
                   }

    link_status = False
    for server in SERVER_LIST.keys():
        ip = SERVER_LIST[server]['ip']
        port = SERVER_LIST[server]['port']
        link_status = alive_status(ip, port)

        if link_status == True:
            log.info('Connected with {}'.format(server))
            return True
            break
        else:
            log.info('Couldnt establish connection with {}'.format(server))
    return link_status

if __name__ == "__main__":
    # - - - - - - - first check - - - - - - - #
    log.info('# - - - - - - STARTING SAFECONN v1 - - - - - - #')
    if linkStatus() == False:
        if findWvdial() == False:
            spawnDaemon(run_wvdial)
        else:
            kill('wvdial')
            time.sleep(1)
            spawnDaemon(run_wvdial)
        #TODO here i would set a iswvdialhere? func in case we habe to cahnge to wvdial infraestructuras1, 2, 3...
        time.sleep(60)
        delroute()
        addroute()
    # - - - - - - - second check - - - - - - - #

        if linkStatus() == False:
            #TODO modem reset or reset of every port i can reach with ttyUSB (no fail allowed)
            for port in range(10):
                restart_modem(port)
            time.sleep(10)
            log.info('Resetting usb')
            reset_USB_Device()

            time.sleep(60)

            spawnDaemon(run_wvdial)
            time.sleep(60)
            delroute()
            addroute()
    # - - - - - - - third check - - - - - - - #

            if linkStatus() == False:
                safeReboot()
                pass


