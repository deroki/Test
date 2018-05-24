import multiprocessing.dummy
import os

devices_down = 0

def ping(ip):
    global devices_down
    out = os.system('ping' + " " + ip)
    if out == 0:
        devices_down += 1
        print("Equipos caidos hasta ahora   " + str(devices_down))
    else:
        pass

def checkping(ip_list):
    pool_pings = multiprocessing.dummy.Pool(200)
    pool_pings.map(ping, ip_list)

ip_down_list = []

with open("ipstable.txt", "r") as file:
    for line in file:
        split_line = line.split('\t')
        print(split_line)
        if split_line[2] == "Zener":
            ip = split_line[1]
            ip_down_list.append(ip)


checkping(ip_down_list)
print(devices_down)

