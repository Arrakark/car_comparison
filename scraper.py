from bs4 import BeautifulSoup
import csv,os,time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from random import randint
from time import sleep
import sys


file_name = sys.argv[1]
domain = 'https://www.rockauto.com'

file = os.path.isfile(file_name)

# set scraping delays
# minimum delay in seconds
min_scraping_delay = 3
# maxinum delay in seconds
max_scraping_delay = 18


fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
browser = webdriver.Firefox(firefox_options=fireFoxOptions)
browser.set_window_size(1222,1205)

def requestUsingProxies(url):
    sleep_time = randint(min_scraping_delay, max_scraping_delay)
    print('Waiting {} seconds'.format(sleep_time))
    sleep(sleep_time)
    browser.get(url)
    return browser.page_source

def findAnchor(input):
    if input is None:
        url = domain
    else:
        url = domain+input['href']
    source = requestUsingProxies(url)
    soup = BeautifulSoup(source, 'lxml')
    output = soup.findChildren('a', class_='navlabellink nvoffset nimportant')
    output = output + soup.findChildren('a', class_='navlabellink nvoffset nnormal')
    return output

brands_we_want = [
'ACURA',
'AUDI',
'BMW',
'CHEVROLET',
'CHRYSLER',
'DAEWOO',
'DODGE',
'FIAT',
'FORD',
'GMC',
'HONDA',
'HYUNDAI',
'INFINITI',
'ISUZU',
'JEEP',
'KIA',
'LAND ROVER',
'LEXUS',
'LINCOLN',
'MAZDA',
'MERCEDES-BENZ',
'MINI',
'MITSUBISHI',
'NISSAN',
'PONTIAC',
'SATURN',
'SMART',
'SUBARU',
'SUZUKI',
'TOYOTA',
'VOLKSWAGEN',
'VOLVO'
]

years_we_want = list(map(str, range(2005,2018)))

with open(file_name, 'a', newline='') as csvfile:
    fieldnames = ['Brand', 'Year','Model','Engine','Category','SubCategory','Manufacturer','PartNumber','MoreDetails','Price']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
    if not file:
        writer.writeheader()

    brands = findAnchor(None)
    for brand in brands:
        if brand.text not in brands_we_want[1:]:
            continue
        years=findAnchor(brand)
        for year in years[1:]:
            if year.text not in years_we_want[1:]:
                 continue
            models=findAnchor(year)
            for model in models[2:]:
                engines=findAnchor(model)
                for engine in engines[3:]:
                    categories = findAnchor(engine)
                    for category in categories[4:]:
                        sub_category_source = requestUsingProxies(domain + category['href'])
                        sub_category_soup = BeautifulSoup(sub_category_source, 'lxml')
                        sub_categories = sub_category_soup.findChildren('a', class_='navlabellink nvoffset nimportant')
                        if len(sub_categories) == 0:
                            sub_categories = sub_category_soup.findChildren('a', class_='navlabellink nvoffset nnormal')
                            sub_categories=sub_categories[5:]

                        for sub_category in sub_categories:
                            details_source = requestUsingProxies(domain + sub_category['href'])
                            myElem = WebDriverWait(browser, 4).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-inner')))
                            for i in myElem:
                                soup = BeautifulSoup(i.get_attribute('innerHTML'), 'lxml')
                                manufracturer = soup.findChild('span', class_='listing-final-manufacturer')
                                partnumber = soup.findChild('span', class_='listing-final-partnumber')
                                details = soup.findChild('span', class_='span-link-underline-remover')
                                more_details = soup.findChild('div', class_='listing-text-row')
                                if details is None:
                                    details='N/A'
                                else:
                                    details=details.text
                                if more_details is None:
                                    more_details='N/A'
                                else:
                                    more_details=more_details.text

                                more_details = details+more_details
                                price = soup.findChild('span', class_='listing-price')
                                print(f'{brand.text}--,{year.text},'
                                      f'--{model.text}--{engine.text}--{category.text}--{sub_category.text}-'
                                      f'-{manufracturer.text}--{partnumber.text}-{more_details}-{price.text}')

                                writer.writerow({'Brand': brand.text, 'Year':year.text, 'Model':model.text, 'Engine':engine.text,
                                        'Category':category.text, 'SubCategory':sub_category.text, 'Manufacturer':manufracturer.text,
                                        'PartNumber':partnumber.text, 'MoreDetails':more_details, 'Price':price.text})
