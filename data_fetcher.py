from selenium import webdriver
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome()
driver.get('https://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp')

initial_date = '2019.03.06'
date_select = Select(driver.find_element_by_name('Fecha'))
date_select.select_by_value(initial_date)

currency_select = Select(driver.find_element_by_name('Moneda'))
currency_select.select_by_value('2')

see_button = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/form/div[3]/button')
see_button.click()



