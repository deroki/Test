from sitechecker import siteChecker
from sitechecker import sshSession
import os
import logging
import logging.handlers
import time
import pprint

def setupLogger(name):
    #check if log dir and file is created:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    log_dir = os.path.join(dir_path,'logs')
    # create log folder if it doesnt exist
    if os.path.isdir(log_dir) == False:
        os.mkdir(log_dir)

    log = logging.getLogger('ConnSafe')
    log.setLevel(logging.DEBUG)

    log_format = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    size_handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, name),
                                  mode='a',
                                  maxBytes=1000000,
                                  backupCount=5,
                                  encoding='utf-8',
                                  delay=0)

    size_handler.setLevel(logging.DEBUG)
    size_handler.setFormatter(log_format)
    log.addHandler(size_handler)
    return log

log = setupLogger('desponibilidad.log')

check = siteChecker()
all_sites = check.getFromWeb()
sites = check.get_from_excel('siteTexts/madridprueba.txt')
print('sites del archivo')
pprint.pprint(sites)
sites_ip = {}
for site in sites.keys():
    try:
        sites_ip[site] = all_sites[site]
    except KeyError:
        print('el site {} no está en la lista total'.format(site))
print("site del diccionario final")
pprint.pprint(sites_ip)
checker = siteChecker()
sitecounter = {}
counter = 0
sitedisponibilidad = {}

def multialive(listeddict):
    site = listeddict[0]
    ip = listeddict[1]['ip']
    if checker.alive_status(ip, 80) == True:
        try:
            sitecounter[site] += 1
        except KeyError:
            sitecounter[site] = 1

while(True):
    print("comenzando")
    counter += 1
    checker.runMultiCheck(sites_ip,multialive)

    for site in sitecounter.keys():
        sitedisponibilidad[site] = sitecounter[site] / counter


    pprint.pprint(sitedisponibilidad)
    time.sleep(10)