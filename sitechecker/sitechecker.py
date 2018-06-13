import multiprocessing.dummy
from multiprocessing.pool import  ThreadPool
import os
import site

import paramiko
import socket
import pprint
import csv
import requests
import vars
import dataset
import time
from sqlalchemy.exc import IntegrityError
from collections import OrderedDict
import pysftp
from types import MethodType
import shelve

class siteChecker(object):

    def __init__(self,list_dict_sites = []):
        self.list_dict_sites = list_dict_sites
        self.result = {}
        self.totalsites = 0
        self.db = dataset.connect('sqlite:///sites.db')

    def create_table(self):
        try:
            print("creando tabla")
            self.db.create_table('sites','site')
        except:
            print(" -- Table sites found -- ")

    def get_from_excel(self, filename):
        site_dict = {}
        with open(filename, "r") as file:
            for line in file:
                try:
                    split_line = line.split('\t')
                    print(split_line)
                    ip = split_line[3]
                    site = split_line[0]
                    site_dict[site] = {'ip' : ip}
                except:
                    pass
                    #TODO logging no se puede meter en la lista de sites
        return site_dict

    def alive_status(self, ip, port):
        try:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.connect((ip, port))
            return True
        except:
            return False


    def runCheck_dict(self,site_list):   # it comes like this --> ('CE1005', {'ip': '10.226.37.40', 'date': '2018-01-12T23:00:37.000Z'})
        """
        Takes a nested dict and check some functions on the sites
        :param site_list:
        """
        print("checking")
        print(site_list)
        ip = site_list[1]['ip']
        site = site_list[0]
        check_dict = {}
        check_dict['ip'] = ip
        if self.alive_status(ip, 80) == True:
            check_dict['alive'] = True
            for intento in range(15):
                try:
                    try:
                        ssh = sshSession(ip, "admin", '0r@nge')
                    except:
                        ssh = sshSession(ip, 'pi', 'raspberry')
                    if ssh:
                        check_dict['ssh'] = True
                        check_dict['ntp'] = ssh.ntp_config()
                        check_dict['i2c'] = ssh.i2c_status()
                        check_dict['cron'] = ssh.cron()
                        ssh.close()
                    else:
                        check_dict['ssh'] = False
                    break
                except Exception as e:
                    print(e)
                    print("Fallo de proceso en site {} reintento {}".format(site, intento))
                    time.sleep(3)
                    continue
        else:
            check_dict['alive'] = False
        self.result[site] = check_dict
        self.counter += 1
        print("{} Checked. Quedan {}".format(site, self.totalsites - self.counter))

    def runMultiCheck(self, sites_dict, func):
        '''Takes a nested dict and convert it to a listed list of items and send one by one
        to the function
        The functions leaves all in the result variable and return it
        '''
        self.counter = 0
        self.result = {}
        self.totalsites = len(sites_dict)
        print("site totales" + str(self.totalsites))
        iterations = 400
        pool = multiprocessing.dummy.Pool(iterations)
        start = 0
        # for i in range((len(dictsites) // iterations) + 1):
        #     print("Round  " + str(i))
        #     start = i * iterations
        #     end = (i + 1) * iterations
        #     pool.map(self.runCheck_dict, list(sites_dict.items())[start:end])
        #     pool.close()
        #     pool.join()
        pool.map(func, list(sites_dict.items()))
        pool.close()
        pool.join()
        pprint.pprint(self.result)
        return self.result

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
        " :returns a nested dict"
        Web_dict = {}
        datatables_url = vars.json_query
        json_response_dict = requests.get(datatables_url).json()
        siteslist_list = json_response_dict['data']
        print('Total sites  ' + str(len(siteslist_list)))
        for sitelist in siteslist_list:
            sitedict = {}
            if sitelist[2] != 1:            #si el fabricante es thaumat es 1
                site= sitelist[0]
                ip= sitelist[1]
                date = sitelist[15]
                Web_dict[site] = {"ip" : ip, 'date' : date}
        print("Total zener sites  " + str(len(Web_dict)))
        return Web_dict

    def list2dict(self, siteslist):
        savedict = {}
        for sitedict in siteslist:
            site = sitedict['site']
            sitedict.pop('site')
            savedict[site] = sitedict
        return savedict

    def save(self, table, sites_dict):
        for retry in range(10):
            try:
                db_list = []
                with dataset.connect('sqlite:///sites.db') as db:
                    table = db[table]
                    for site, siteFeatures in sites_dict.items():
                        dict = siteFeatures
                        dict['site'] = site
                        table.upsert(dict, ['site'])
                        print("table {} modified".format(table))
                    break
            except:
                continue

    def GetTable(self,tab):
        dic = {}
        with dataset.connect('sqlite:///sites.db') as db:
            table = db[tab]
            for row in table.all():
                site = row['site']
                row.pop('site')
                dic[site] = dict(OrderedDict(row))
        return dic

    def CompareDicts(self,dictDB,dictNew,features):
        print(dictDB)
        print(dictNew)
        for site in dictNew.keys():
            if site not in dictDB.keys(): # if site wasnt before add to db
                dictDB[site] = dictNew[site]
                continue
            for feat in dictNew[site].keys(): # feats of every site in newdict
                if feat in features:
                    featc_field = feat + "_c"
                    # the feat didnt exist before in db
                    if feat not in dictDB[site].keys():
                        dictDB[site][feat] = dictNew[site][feat]
                        dictDB[site][featc_field] = 1
                    # feat exist
                    else:
                        print("{} was before".format(feat))
                        # different value
                        if dictDB[site][feat] != dictNew[site][feat]:
                            dictDB[site][feat] = dictNew[site][feat]
                            if dictDB[site][feat] == None:
                                continue
                            try:
                                dictDB[site][featc_field] += 1
                            except (KeyError,TypeError):
                                dictDB[site][featc_field] = 1
                        # same value
                        else:
                            pass

        return  dictDB

    def Scan(self, table, length = None, province = None):
        NewDict = self.getFromWeb()
        if province:
            NewDict = {k: v for k, v in NewDict.items() if k.startswith(province)}
        NewDict = list(NewDict.items())[:length]
        NewDict = {k: v for row in NewDict for k, v in NewDict}
        self.runMultiCheck(NewDict)
        NewDict = self.result
        DbDict = self.GetTable(table)
        FinalDict = self.CompareDicts(DbDict, NewDict, ['ssh', 'alive','i2c'])
        pprint.pprint(FinalDict)
        self.save(table, FinalDict)
        # dict = {k : v for row in dict for k, v in row}
        # dict_final = {}
        # for k, v in dict:
        #     print(k)
        #     print(v)
        #     dict_final[k] = v
        # print(len(dict_final))
        # pprint.pprint(dict_final)
        # self.runMultiCheck2(dict_final)
        # self.save("test5", self.result)

class sshSession(paramiko.SSHClient):
    def __init__(self, ip, user, password, site,  timeout = 30):
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(hostname= ip, username=user, password=password, timeout=timeout)
        self.user = user
        self.ip = ip
        self.site = site
        self.password = password
        self.timeout = timeout
        self.sftp = self.open_sftp()
        self.sftp.put_dir = MethodType(self.MySFTPClient.put_dir, self.sftp)
        self.sftp.mkdir = MethodType(self.MySFTPClient.mkdir, self.sftp)
    def i2c_status(self):
        try:
            stdin, stdout, stderr = self.exec_command("sudo timeout 5 /usr/sbin/i2cdetect -y 1")
            stdouttuple = stdout.readlines()

            if len(stdouttuple) < 4:
                return False
            else:
                return True
        except:
            return None

    def ntp_config(self):
        try:
            sftp = self.open_sftp()
            sftp.put("ntp.conf", "/home/admin/ntp.conf")
            self.exec_command("sudo mv -f /home/admin/ntp.conf /etc/ntp.conf")
            self.exec_command("sudo service ntp restart")
            self.exec_command("ntpq -pn")
            return True
        except:
            return None

    def cron(self):
        # check crontab -l
        stdin, stdout, stderr = self.exec_command('crontab -l', timeout=60)
        crontab_out = ''
        #crontab out
        for index, line in enumerate(stdout.readlines()):
            if line is not "":
                crontab_out += line
        stderr_string = ""
        #crontab err
        for index, line in enumerate(stderr.readlines()):
            if line is not "":
                stderr_string += line
                print(line.rstrip('\n'))
        if stderr_string != "":
            print("Stderr is\n%s" % (stderr_string.rstrip('\n')))
        #crontab wrote before?
        needs_change = "sudo reboot now" not in crontab_out
        print('needs_change? {}'.format(needs_change))
        # crontab wrote
        if not needs_change:
            return "Done before"
        # not wrote, so we change writing this on console
        new_cron = "{}\n@reboot sleep {} && sudo reboot now &".format(crontab_out, 6 * 60 * 60)
        stdin, stdout, stderr = self.exec_command(
            'echo "{0}" > /home/{1}/new_cron && crontab -u {1} /home/{1}/new_cron && sudo service cron restart'.format(new_cron,self.user),
            timeout=60)
        stdout_string = ""
        for index, line in enumerate(stdout.readlines()):
            if line is not "":
                stdout_string += line
        stdin.write(self.password + '\n')
        stdin.flush()
        print(stdout.read())
        print("el stdout del echo en crontab: " + stdout_string)
        return "Done now"

    def newCron(self,linebefore, newcronlines):
        """
        Function that change cron with new lines
        :param linebefore: Line that checks if happened before
        :param newcronlines: object
        :return True-> done
                False-> not done
        """

        def cronNow():
            stdin, stdout, stderr = self.exec_command('crontab -l', timeout=60)
            crontab_out = ''
            for line in stdout.readlines():
                if line not in ["\n", ""]:
                    crontab_out += line
            return crontab_out

        # crontab wrote before?
        cronnow = cronNow()
        print('{} cron before is {}'.format(self.site, cronnow))
        crontab_out = cronnow
        if linebefore not in crontab_out:
            print("Change need, line {0} wasnt before".format(linebefore))
            #plug together cronold + newlines
            new_cron = "{0}\n{1}".format(crontab_out, newcronlines)
            changecron = 'echo "{0}" >  ' \
                            '/home/{1}/new_cron && crontab  ' \
                            '-u {1} /home/{1}/new_cron  ' \
                            '&& sudo service cron restart'.format(new_cron,self.user)
            stdin, stdout, stderr = self.exec_command(changecron,timeout=60)
            crontab_out = ''
            # crontab out
            for line in stdout.readlines():
                if line is not "":
                    crontab_out += line
            print('''Before newcron insertion, this is the stdout: 
                    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                    {0}
                    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                    '''.format(crontab_out))
            stdin.write(self.password + '\n')
            stdin.flush()
            print('{} cron after is {}'.format(self.site, cronNow()))
            return True
        else:
            print("Change not need, line was before")
            return False

    def changeFile(self,filepath,remotefile):
        filename = filepath.split('/')[-1]

        tempfile = "/home/{0}/{1}".format(self.user,filename)
        try:

            print("uploading file...")
            self.sftp.put(filepath, tempfile)
            print("moving file in remote")
            stdin, stdout, stderr = self.exec_command("sudo mv -f {0} {1}".format(tempfile,remotefile))
            print(stdout.readlines())
            #stdin.write(self.password + '\n')
            #stdin.flush()
        except Exception as e:
            print(e)
            return None

    def put_dir(self, source, target):

        self.sftp.put_dir(source,target)

    class MySFTPClient(paramiko.SFTPClient):
        def put_dir(self, source, target):
            ''' Uploads the contents of the source directory to the target path. The
                target directory needs to exists. All subdirectories in source are
                created under target.
            '''
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    self.put(os.path.join(source, item), '%s/%s' % (target, item))
                else:
                    self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

        def mkdir(self, path, mode=511, ignore_existing=False):
            ''' Augments mkdir by adding an option to not fail if the folder exists  '''
            try:
                paramiko.SFTPClient.mkdir(self,path, mode)
            except IOError:
                if ignore_existing:
                    pass
                else:
                    raise

        # "@reboot sleep 20 && sudo python2.7 /var/www/SmartsiteClient/cron/meta_cron.py &"
        # "@reboot sleep 20 && sudo python2.7 /var/www/SmartsiteClient/cron/meta_cron.py &\n@reboot sleep {} && sudo reboot now &"
        # '''echo "@reboot sleep 20 && sudo python2.7 /var/www/SmartsiteClient/cron/meta_cron.py &
        #
        # @reboot sleep 21600 && sudo reboot now &" > /home/admin/new_cron && crontab -u admin /home/admin/new_cron '''





if __name__ == "__main__":

    # mychecker = siteChecker()
    # print("hi")
    # dictsites = mychecker.getFromWeb()
    # print("aqui")
    # #dictsites = mychecker.get_from_excel("ipstable.txt")
    # mychecker.runMultiCheck2(dictsites)
    # print(mychecker.result)
    def checkprueba():
        dict_text = {"orange" : {'ip': "10.226.37.21"},
                'le1738' : {'ip' : '10.226.38.49'},
                'SE0027' : {'ip' : '10.226.39.31'}}

        checker = siteChecker()
        checker.Scan('test_5_1')

    def UpdateSafeConn(nesteddict, name):
        sites = nesteddict
        pprint.pprint(sites)
        with shelve.open('shelve.db','c') as shelf:
            savedsites = shelf[name]

            sites = {
                'pcr3': {'ip' : '10.226.37.21'},
                'raspberry' : {'ip' : '192.168.1.1'}
            }
            # takes a nest dict from text

            for site in sites.keys():

                print(" - - - - - - - FIXING SITE  {} - - - - - - - ".format(site) )
                print(" - - - - - - - Getting session  - - - - - - - ")
                ip = sites[site]['ip']
                ssh = sshSession(ip, 'admin', '0r@nge', site)
                #change wvdial file
                print(" - - - - - - -  Uploading wvdial  - - - - - - - ")
                ssh.changeFile('files/wvdial.conf','/etc/wvdial.conf')
                #Upload dir Conectivity Safe
                print(" - - - - - - -  Uploading Conectivity safe  - - - - - - - ")
                try:
                    ssh.sftp.mkdir('/var/www/SmartsiteClient/DjangoServer/ConectivitySafe')
                except:
                    print('Puede que la carpeta ya exista')
                ssh.put_dir('files/ConectivitySafe', '/var/www/SmartsiteClient/DjangoServer/ConectivitySafe')
                #new cron lines:
                print(" - - - - - - -  Changing cron  - - - - - - - ")
                before = '/var/www/SmartsiteClient/DjangoServer/ConectivitySafe/ConectivitySafeModule.py'
                newcronlines = '''*/5 * * * * sudo python3 /var/www/SmartsiteClient/DjangoServer/ConectivitySafe/ConectivitySafeModule.py &'''
                ssh.newCron(before, newcronlines )

                shelf[name][site] = True
                pprint.pprint(shelf[name])
                input("Press Enter to continue...")


    check = siteChecker()
    sites = check.get_from_excel('siteTexts/madridprueba.txt')
    UpdateSafeConn('siteTexts/madridprueba.txt')














