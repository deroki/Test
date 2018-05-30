import multiprocessing.dummy
import os
import paramiko
import socket
import pprint


class siteChecker(object):


    def __init__(self,list_dict_sites = []):
        self.list_dict_sites = list_dict_sites

    def get_from_excel(self, filename):
        with open(filename, "r") as file:
            for line in file:
                try:
                    split_line = line.split('\t')
                    print(split_line)
                    ip = split_line[3]
                    site = split_line[0]
                    site_dict = {"ip": ip, "site": site}
                    self.list_dict_sites.append(site_dict)
                except:
                    pass
                    #TODO logging no se puede meter en la lista de sites

    def alive_status(self, ip, port):
        try:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.connect((ip, port))
            return True
        except:
            return False


    def sshSession(self, ip, user, password, timeout = 30):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname= ip, username=user, password=password, timeout=timeout)
            return self.ssh_client
        except:
            return None

    def i2c_status(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("sudo timeout 5 /usr/sbin/i2cdetect -y 1")
            stdouttuple = stdout.readlines()

            if len(stdouttuple) < 4:
                return False
            else:
                return True
        except:
            return "Error"

    def ntp_config(self):
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put("ntp.conf", "/home/admin/ntp.conf")
            self.ssh_client.exec_command("sudo mv -f /home/admin/ntp.conf /etc/ntp.conf")
            self.ssh_client.exec_command("sudo service ntp restart")
            self.ssh_client.exec_command("ntpq -pn")
            return True
        except:
            return "Error"

    def runCheck_dict(self,site_dict):
        ip = site_dict['ip']
        site = site_dict['site']
        check_dict = {'site' : site}
        if self.alive_status(ip, 80) == True:
            check_dict['alive'] = False
            try:
                ssh = self.sshSession(ip, "admin", '0r@nge')
            except:
                shh = self.sshSession(ip, 'pi', 'raspberry')
            if ssh:
                check_dict['ssh'] = True
                check_dict['ntp'] = self.ntp_config()
                check_dict['i2c'] = self.i2c_status()
            else:
                check_dict['ssh'] = False
        else:
            check_dict['alive'] = False

        self.final_list_dict.append(check_dict)




    def runMultiCheck(self):
        self.final_list_dict = []
        pool = multiprocessing.dummy.Pool(200)
        pool.map(self.runCheck_dict, self.list_dict_sites)
        pprint.pprint(self.final_list_dict)








