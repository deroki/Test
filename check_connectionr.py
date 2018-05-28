import multiprocessing.dummy
import os
import pprint
import paramiko
import socket
import csv
import pandas

devices_down = 0
devices_really_down = []
devices_up = []
devices_up_ssh = []




def listdict_to_csv(listdicts, csvname):
    with open(csvname, 'w') as csvfile:
        csv_columns = listdicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames = csv_columns, lineterminator='\n' )
        writer.writeheader()
        for dict in listdicts:
            writer.writerow(dict)


def try_ssh(site_dict):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=site_dict['ip'],username='admin',password='0r@nge', timeout=30)

        # change ntp server
        try:
            sftp = ssh_client.open_sftp()
            sftp.put("ntp.conf", "/home/admin/ntp.conf")
            stdin, stdout, stderr = ssh_client.exec_command("sudo mv -f /home/admin/ntp.conf /etc/ntp.conf")
            stdin, stdout, stderr = ssh_client.exec_command("sudo service ntp restart")
            stdin, stdout, stderr = ssh_client.exec_command("ntpq -pn")
            print(stdout.readlines())
        except Exception as e:
            print(e)
            print("no se pudo cambiar el ntp")
        # check i2c
        try:
            stdin, stdout, stderr = ssh_client.exec_command("timeout 5 /usr/sbin/i2cdetect -y 1")
            stdouttuple = stdout.readlines()
            pprint.pprint(stdouttuple)
            print(len(stdouttuple))
            if len(stdouttuple) < 3:
                print("no hay i2c")
                site_dict['i2c'] = False
            else:
                print("hay i2c")
                site_dict['i2c'] = True
        except:
            print("no se puede comprobar i2c")
        # insert in the list ssh
        devices_up_ssh.append(site_dict)
    except Exception as e:
        pass

def ping(site_dict):
    global devices_down

    try:
        _socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        _socket.connect((site_dict['ip'], 80))
        devices_up.append(site_dict)
        try_ssh(site_dict)
    except:
        devices_down += 1
        devices_really_down.append(site_dict)
        print("Equipos caidos hasta ahora   " + str(devices_down))

def checkping(sites_list):
    pool_pings = multiprocessing.dummy.Pool(200)
    pool_pings.map(ping, sites_list)

#--------------------    MAIN ------------------------· #

ip_down_list = []

# import sqlite3
# conection = sqlite3.connect("pcr.sqlite")
# select_all_host = conection.execute("select host from pcr")
# for host in select_all_host:
#     print(host[0])
#     ip_down_list.append(host[0])

with open("ipstable.txt", "r") as file:
    for line in file:
        split_line = line.split('\t')
        print(split_line)
        if split_line[2] == "Zener":
            ip = split_line[1]
            site = split_line[0]
            site_dict = {"ip" : ip, "site" : site}
            ip_down_list.append(site_dict)

with open("Caidos.csv", 'r') as csvfile:
    csvtuple = csv.DictReader(csvfile)
    for row in csvtuple:
        site = row['Site']
        ip = row['IP']
        site_dict = {'site' : site,
                     'ip' : ip}
        ip_down_list.append(site_dict)

checkping(ip_down_list)
print(devices_down)
pprint.pprint(devices_really_down)
print("devices con ping")
pprint.pprint(devices_up)
print(""" Dispositivos con ping y ssh  

""")
pprint.pprint(devices_up_ssh)
try:
    listdict_to_csv(devices_up_ssh,"up_n_ssh.csv")
except:
    print("no hay nada que meter en el diccionario")

print("totales {}".format(len(devices_up_ssh)))
