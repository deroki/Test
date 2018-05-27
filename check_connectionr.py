import multiprocessing.dummy
import os
import pprint
import paramiko
import socket

devices_down = 0
devices_really_down = []
devices_up = []
devices_up_ssh = []

def try_ssh(ip):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip,username='admin',password='0r@nge', timeout=30)
        devices_up_ssh.append(ip)
    except Exception as e:
        pass

def ping(ip):
    global devices_down
    try:
        _socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        _socket.connect((ip, 80))
        devices_up.append(ip)
        try_ssh(ip)
    except:
        devices_down += 1
        devices_really_down.append(ip)
        print("Equipos caidos hasta ahora   " + str(devices_down))

def checkping(ip_list):
    pool_pings = multiprocessing.dummy.Pool(200)
    pool_pings.map(ping, ip_list)

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
            ip_down_list.append(ip)


checkping(ip_down_list)
print(devices_down)
pprint.pprint(devices_really_down)
print("devices con ping")
pprint.pprint(devices_up)
print(""" Dispositivos con ping y ssh  

""")
pprint.pprint(devices_up_ssh)

print("totales {}".format(len(devices_up_ssh)))
