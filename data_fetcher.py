from datetime import date, timedelta, datetime
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import csv


def collect_data(xpath, driver, collection):
    """
    It inspects the table with the currency exchange found at the webpage and collects all the relevant information
    from a table row: date, value, currency fluctuation with regards to the previous day, weekday and if the day occurs
    after a holiday. All these data are stored in a dictionary.
    :param xpath: xpath to the row of the data table
    :type xpath: str
    :param driver: Chrome driver
    :type driver: Webdriver
    :param collection: collection of data dictionaries stored so far
    :type collection: list
    :return: data dictionary of the day corresponding to the table row
    :rtype: dict
    """
    day_data = {}
    date_ = datetime.strptime(driver.find_element_by_xpath(xpath + '/td[1]').text, '%d/%m/%Y').date()
    day_data['day'], day_data['month'], day_data['year'] = date_.day, date_.month, date_.year
    day_data['value'] = round(float(driver.find_element_by_xpath(xpath + '/td[3]').text.replace(',', '.')), 4)

    if not collection:
        day0_xpath = '/html/body/div/div[2]/div/div/div/table/tbody/tr[1]'
        prev_day_val = round(float(driver.find_element_by_xpath(day0_xpath + '/td[3]').text.replace(',', '.')), 4)
        prev_day_date = datetime.strptime(driver.find_element_by_xpath(day0_xpath + '/td[1]').text, '%d/%m/%Y').date()
    else:
        prev_day = collection[-1]
        prev_day_val = prev_day['value']
        prev_day_date = date(prev_day['year'], prev_day['month'], prev_day['day'])

    day_data['delta'] = round(day_data['value'] - prev_day_val, 4)
    day_data['increase'] = 1*(day_data['delta'] > 0)
    day_data['weekday'] = date_.weekday()
    day_data['after holiday'] = 0
    if (day_data['weekday'] and prev_day_date != date_ - timedelta(days=1)) or \
            (not day_data['weekday'] and prev_day_date != date_ - timedelta(days=3)):
        day_data['after holiday'] = 1

    return day_data


def build_csv(collection):
    with open('data.csv', 'w+', newline="") as f:
        file_writer = csv.writer(f, dialect='excel', delimiter=';')
        file_writer.writerow(['Day', 'Month', 'Year', 'Value', 'Delta', 'Increase', 'Weekday', 'After Holiday'])
        for elem in collection:
            file_writer.writerow([elem['day'], elem['month'], elem['year'], elem['value'], elem['delta'],
                                  elem['increase'], elem['weekday'], elem['after holiday']])


c_options = webdriver.ChromeOptions()
c_options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=c_options)
driver.get('https://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp')

years_back = 1
today = date.today()
initial_date = today - timedelta(days=365*years_back+1)

# initial_date = '2019.03.17'

date_select = Select(driver.find_element_by_name('Fecha'))
while True:
    try:
        date_select.select_by_value(date.strftime(initial_date, '%Y.%m.%d'))
    except NoSuchElementException:
        initial_date += timedelta(days=1)
    else:
        break


currency_select = Select(driver.find_element_by_name('Moneda'))
currency_select.select_by_value('2')

see_button = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/form/div[3]/button')
see_button.click()
sleep(1)
data = []
i = 2
while True:
    try:
        xp = '/html/body/div/div[2]/div/div/div/table/tbody/tr[{}]'.format(i)
        data.append(collect_data(xp, driver, data))
        i += 1
        print(data[-1])
    except NoSuchElementException:
        break
    finally:
        if i >= 10:
            break
driver.quit()
build_csv(data)






