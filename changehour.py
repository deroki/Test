import os, time, sys
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

ip_list = []
# with open("ips.txt", "r") as f:
#     print(f)
#     for i in f:
#         print(i)
#         ip_list = i.split(',')
# print(ip_list)
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
chrome_driver = dir_path + "\chromedriver.exe"
driver = webdriver.Chrome(chrome_driver)

with open("ipstable.txt", "r") as file:
    with open("downip.txt", 'w') as output:
        for line in file:
            split_line = line.split('\t')
            print(split_line)
            if split_line[2] == "Zener":
                ip = split_line[1]

                try:
                    driver.get("http://" + ip + "/login/")
                    time.sleep(5)

                    driver.find_element_by_id("username").click()
                    driver.find_element_by_id("username").clear()
                    driver.find_element_by_id("username").send_keys("admin")
                    driver.find_element_by_id("password").clear()
                    driver.find_element_by_id("password").send_keys("0r@nge!!")
                    driver.find_element_by_xpath("//button[@type='submit']").click()
                    driver.find_element_by_link_text("Fecha").click()
                    driver.find_element_by_xpath("//input[@value='Guardar']").click()
                except:
                    print("no conecta   " + ip)
                    output.write(line)

