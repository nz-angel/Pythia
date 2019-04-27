from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from datetime import date, timedelta
import os
from time import sleep
import pandas as pd
import numpy as np


def date_to_str(dt):
    return '{}.{:0>2d}.{:0>2d}'.format(dt.year,dt.month,dt.day)


c_options = webdriver.ChromeOptions()
# c_options.headless = True
c_options.add_argument('window-size=0x0')
new_options = {'download.default_directory' : os.getcwd()}
c_options.add_experimental_option('prefs', new_options)
driver = webdriver.Chrome(chrome_options=c_options)
driver.get('https://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp')

years_back = 1
today = date.today()
initial_date = today - timedelta(days=365*years_back)

# initial_date = '2019.03.17'

date_select = Select(driver.find_element_by_name('Fecha'))
while True:
    try:
        date_select.select_by_value(date_to_str(initial_date))
    except NoSuchElementException:
        initial_date += timedelta(days=1)
    else:
        break


currency_select = Select(driver.find_element_by_name('Moneda'))
currency_select.select_by_value('2')

see_button = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/form/div[3]/button')
see_button.click()

excel_file = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/a').click()
sleep(2)
driver.quit()

dollar_df = pd.read_html('CotizacionesBCRA.xls')
print()


