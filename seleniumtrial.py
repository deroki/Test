import os, time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
chrome_driver = dir_path + "\chromedriver.exe"

driver = webdriver.Chrome(chrome_driver)
# opts = FirefoxOptions()
# opts.add_argument("--headless")
#
# dir_path = os.path.dirname(os.path.realpath(__file__))
# firefox_driver = dir_path + "/geckodriver"
# driver = webdriver.Firefox(executable_path=firefox_driver, firefox_options=opts)
driver.get('http://10.118.214.115:8080/clima')
user_input = driver.find_element_by_name("j_username")
user_input.send_keys("zener")

password_input = driver.find_element_by_name('j_password')
password_input.send_keys("zener")


boton = driver.find_element_by_xpath("//button[@type='submit']")
boton.click()
#buscar el pcr
driver.get("http://10.118.214.115:8080/clima/admin/mediacion/")
#driver.find_element_by_link_text(u"Equipos Mediación").click()
driver.find_element_by_xpath("//input[@type='search']").send_keys(Keys.ENTER)
driver.find_element_by_xpath("//input[@type='search']").clear()
driver.find_element_by_xpath("//input[@type='search']").send_keys("mx0112")
time.sleep(4)
driver.find_element_by_xpath("//table[@id='tabla']/tbody/tr/td[3]").click()
#
driver.find_element_by_id("agregarAlarma").click()
time.sleep(3)
driver.find_element_by_id("f_puntoalarma").click()
Select(driver.find_element_by_id("f_puntoalarma")).select_by_visible_text("19")
driver.find_element_by_id("f_puntoalarma").click()
driver.find_element_by_id("f_texto").click()
driver.find_element_by_id("f_texto").clear()
driver.find_element_by_id("f_texto").send_keys("texto")
driver.find_element_by_id("f_textoextendido").click()
driver.find_element_by_id("f_textoextendido").clear()
driver.find_element_by_id("f_textoextendido").send_keys("textoext")
driver.find_element_by_id("f_categoria").click()
Select(driver.find_element_by_id("f_categoria")).select_by_visible_text("Semi-urgente")
driver.find_element_by_id("f_categoria").click()
driver.find_element_by_id("f_inhibida").click()
driver.find_element_by_id("botonGuardar").click()
#
time.sleep(2)
driver.find_element_by_link_text(u"Sondas Tª").click()
driver.find_element_by_id("agregarSonda").click()
time.sleep(3)
driver.find_element_by_id("f_numero").click()
driver.find_element_by_xpath("//option[@value='7']").click()
driver.find_element_by_id("f_nombre").click()
driver.find_element_by_id("f_nombre").clear()
driver.find_element_by_id("f_nombre").send_keys("nombresonda")
driver.find_element_by_id("f_observaciones").clear()
driver.find_element_by_id("f_observaciones").send_keys("observacionsonda")
driver.find_element_by_id("botonGuardar").click()
#
driver.find_element_by_link_text("Contadores").click()
driver.find_element_by_id("agregarContador").click()
driver.find_element_by_id("f_nombre").click()
driver.find_element_by_id("f_nombre").clear()
driver.find_element_by_id("f_nombre").send_keys("nombrecontador")
driver.find_element_by_id("f_numeroModulo").click()
driver.find_element_by_id("f_numeroModulo").click()
driver.find_element_by_id("f_numeroModulo").clear()
driver.find_element_by_id("f_numeroModulo").send_keys("6")
driver.find_element_by_xpath("//input[@id='f_observaciones']").click()
driver.find_element_by_xpath("//input[@id='f_observaciones']").clear()
driver.find_element_by_xpath("//input[@id='f_observaciones']").send_keys("obersacionescontador")
driver.find_element_by_id("f_tipoContador").click()
Select(driver.find_element_by_id("f_tipoContador")).select_by_visible_text(u"Contador Trifásico")
driver.find_element_by_id("f_tipoContador").click()
driver.find_element_by_xpath("(//button[@type='button'])[10]").click()
#driver.quit()