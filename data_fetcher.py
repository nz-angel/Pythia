from datetime import date, timedelta, datetime
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import warnings
import os
import csv


def collect_row_data(xpath, driver, collection, speech_dates):
    """
    It inspects the table with the currency exchange found at the webpage and collects all the relevant information
    from a table row: date, value, currency fluctuation with regards to the previous day, weekday and if the day occurs
    after a holiday. All these data are stored in a dictionary.
    :param speech_dates: set of presidential speeches dates
    :type speech_dates: set
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
    day_data['after speech'] = 1*(date_ - timedelta(days=1) in speech_dates)
    day_data['speech'] = 1*(date_ in speech_dates)

    return day_data


def build_csv(collection):
    """
    Writes the .csv file with the collected data
    :param collection: list with the data dictionaries of each registered day
    :type collection: list
    """
    with open('data.csv', 'w+', newline="") as f:
        file_writer = csv.writer(f, dialect='excel', delimiter=';')
        file_writer.writerow(['Day', 'Month', 'Year', 'Value', 'Delta', 'Increase', 'Weekday', 'After Holiday',
                              'Day of Speech', 'After Speech'])
        for elem in collection:
            file_writer.writerow([elem['day'], elem['month'], elem['year'], elem['value'], elem['delta'],
                                  elem['increase'], elem['weekday'], elem['after holiday'], elem['after speech'],
                                  elem['speech']])


def update_data(end_date, path_to_csv):
    """
    Updates the data stored in an already existing data.csv . Reads the file's latest entry, extracts the date of the
    corresponding day and adds the information of the days until end_date to the file. The function performs no
    changes if the end date is prior to the last date recorded in the file.
    :param end_date: the last day that wants to be recorded
    :type end_date: date
    :param path_to_csv: path to data.csv
    :type path_to_csv: str
    """
    if end_date is None:
        end_date = date.today()
    else:
        end_date = datetime.strptime(end_date, '%d/%m/%Y')

    try:
        with open(os.path.join(path_to_csv, 'data.csv'), 'r', newline='') as f:
            f.seek(0, 2)
            fsize = f.tell()
            f.seek(fsize-60, 0)
            last_entry = list(map(int, f.readlines()[-1].split(';')[:3]))
            initial_date = date(last_entry[2], last_entry[1], last_entry[0]) + timedelta(days=1)
    except FileNotFoundError:
        raise FileNotFoundError('data.csv was not found. Generate the file or specify a correct path')
    else:
        if initial_date >= end_date:
            warnings.warn('Last day recorded is posterior to end_date. No changes performed.')
            return

        new_data = parse_table(initial_date, end_date)
        with open('data.csv', 'a', newline='') as f:
            file_writer = csv.writer(f, dialect='excel', delimiter=';')
            for elem in new_data:
                file_writer.writerow([elem['day'], elem['month'], elem['year'], elem['value'], elem['delta'],
                                      elem['increase'], elem['weekday'], elem['after holiday']])


def parse_table(initial_date, end_date):
    """
    Selenium driver that parses the table found at the website of the Central Bank of Argentina. To access the
    information, it's necessary to set an initial date. In the website, the exchange rate is informed from the initial
    day to the latest bussiness day. If the end date happens to be a non-bussiness day, the information of the
    following business day is recorded. Likewise, if the initial date is not a business day, the information is
    recorded since the first business day following it.
    :param initial_date: initial date from which data wants to be recorded
    :type initial_date: date
    :param end_date: last date to which data wants to be recorded
    :type end_date: date
    :return: list of dictionaries that represent the data obtained from each one of the table's rows
    :rtype: list
    """
    speech_dates = get_speech_dates()

    c_options = webdriver.ChromeOptions()
    c_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=c_options)
    driver.get('https://www.bcra.gob.ar/PublicacionesEstadisticas/Evolucion_moneda.asp')

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
            data.append(collect_row_data(xp, driver, data, speech_dates))
            # print(data[-1])
        except NoSuchElementException:
            break
        else:
            last_date = driver.find_element_by_xpath('/html/body/div/div[2]/div/div/div/table/tbody/tr[{}]/td['
                                                     '1]'.format(i)).text
            i += 1
            if end_date <= datetime.strptime(last_date, '%d/%m/%Y').date():
                break
    driver.quit()
    return data


def get_speech_dates():
    """
    Generates a set of dates of the presidental speeches, obtained from the official data provided by the Pink House
    website.
    :return: set of presidential speeches dates
    :rtype: set
    """
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
              'Noviembre', 'Diciembre']
    month_dict = {month: number for month, number in zip(months, range(1, 13))}
    speech_dates = set([])
    c_options = webdriver.ChromeOptions()
    c_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=c_options)
    driver.get('https://www.casarosada.gob.ar/informacion/discursos')
    while True:
        i = 1
        while True:
            try:
                xpath = '//*[@id="jm-maincontent"]/main/div/section/div/div/div[2]/div[{}]/div/a/div/time'.format(i)
                str_date = driver.find_element_by_xpath(xpath).text
            except NoSuchElementException:
                break
            else:
                str_date = str_date.split()
                date_ = date(int(str_date[5]), month_dict[str_date[3]], int(str_date[1]))
                speech_dates.add(date_)
                i += 1

        try:
            next_button = driver.find_element_by_xpath(
                '//*[@id="jm-maincontent"]/main/div/section/div/div/div[3]/ul/li[13]/a')
        except NoSuchElementException:
            break
        else:
            next_button.click()
    driver.quit()
    return speech_dates


def main(years_back=None, initial_date=None, end_date=None, update=False, path_to_csv=''):
    if update:
        update_data(end_date, path_to_csv)
    else:
        # If no input is defined, the default is setting the initial date to one year ago
        if all(a is None for a in [years_back, initial_date, end_date]):
            years_back = 1

        # years_back overrides other inputs if not None
        if years_back:
            end_date = date.today()
            initial_date = end_date - timedelta(days=365*years_back+1)
        else:
            if initial_date is None and end_date is not None:
                end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
                initial_date = end_date - timedelta(days=365+1)
            elif initial_date is not None and end_date is None:
                end_date = date.today()
            else:
                initial_date = datetime.strptime(initial_date, '%d/%m/%Y').date()
                end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
                if initial_date >= end_date:
                    warnings.warn('Initial date is posterior to end date. Setting the initial date to the day before '
                                  'the end date')
                    initial_date = end_date - timedelta(days=1)

        data = parse_table(initial_date, end_date)
        build_csv(data)


if __name__ == '__main__':
    main()

    



