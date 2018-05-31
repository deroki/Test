import multiprocessing.dummy
import os
import paramiko
import socket
import pprint
import csv
import requests
import vars


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
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname= ip, username=user, password=password, timeout=timeout)
            return ssh_client
        except:
            return None

    def i2c_status(self, client):
        try:
            stdin, stdout, stderr = client.exec_command("sudo timeout 5 /usr/sbin/i2cdetect -y 1")
            stdouttuple = stdout.readlines()

            if len(stdouttuple) < 4:
                return False
            else:
                return True
        except:
            return "Error"

    def ntp_config(self, client):
        try:
            sftp = client.open_sftp()
            sftp.put("ntp.conf", "/home/admin/ntp.conf")
            client.exec_command("sudo mv -f /home/admin/ntp.conf /etc/ntp.conf")
            client.exec_command("sudo service ntp restart")
            client.exec_command("ntpq -pn")
            return True
        except:
            return "Error"

    def runCheck_dict(self,site_dict):
        ip = site_dict['ip']
        site = site_dict['site']
        check_dict = {'site' : site}
        check_dict['ip'] = ip
        if self.alive_status(ip, 80) == True:
            check_dict['alive'] = True
            try:
                ssh = self.sshSession(ip, "admin", '0r@nge')
            except:
                ssh = self.sshSession(ip, 'pi', 'raspberry')
            if ssh:
                check_dict['ssh'] = True
                check_dict['ntp'] = self.ntp_config(ssh)
                check_dict['i2c'] = self.i2c_status(ssh)
            else:
                check_dict['ssh'] = False
        else:
            check_dict['alive'] = False

        self.final_list_dict.append(check_dict)
        print('| ', end='')

    def runMultiCheck(self):
        self.final_list_dict = []
        pool = multiprocessing.dummy.Pool(200)
        pool.map(self.runCheck_dict, self.list_dict_sites)
        pprint.pprint(self.final_list_dict)
        return self.final_list_dict

    def listdict_to_csv(self, listdicts, csvname):
        '''
        Take a list of dicst and create a csv with the header of dict keys
        :param listdicts:
        :param csvname:
        :return:
        '''
        with open(csvname, 'w') as csvfile:
            csv_columns = listdicts[0].keys()
            headers = ['site', 'ip', 'ssh', 'i2c', 'alive', 'ntp']
            writer = csv.DictWriter(csvfile, fieldnames= headers, lineterminator='\n')
            writer.writeheader()
            for dict in listdicts:
                writer.writerow(dict)

    def getFromWeb(self):
        self.final_list_dict = []
        datatables_url = vars.json_query
        json_response_dict = requests.get(datatables_url).json()
        siteslist_list = json_response_dict['data']
        print('Total sites  ' + str(len(siteslist_list)))

        for sitelist in siteslist_list:
            sitedict = {}
            if sitelist[2] != 1:            #si el fabricante es thaumat es 1
                sitedict['site'] = sitelist[0]
                sitedict['ip'] = sitelist[1]
                self.final_list_dict.append(sitedict)
        print("Number of Zener Pcrs  " + str(len(self.final_list_dict)))


if __name__ == "__main__":

    mychecker = siteChecker()
    mychecker.getFromWeb()
    print(mychecker.final_list_dict)







