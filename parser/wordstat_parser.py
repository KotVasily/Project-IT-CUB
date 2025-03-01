import time 
import pickle
import pandas as pd 
import re 
import os 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def convert_date(date_str):
    months = {
        "январь": "01", "февраль": "02", "март": "03", "апрель": "04",
        "май": "05", "июнь": "06", "июль": "07", "август": "08",
        "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12"
    }
    match = re.match(r"(\D+) (\d{4})", date_str)
    if match:
        month, year = match.groups()
        month_num = months.get(month.strip().lower(), "00")  
        return f"{year}-{month_num}"
    return date_str  

def extract_table_to_csv(html: str):
    soup = BeautifulSoup(html, "lxml")
    headers = ["date", "views", "delete"]

    data = []
    for row in soup.find_all("tr")[1:]: 
        cells = row.find_all("td")
        if len(cells) > 0:
            row_data = [cell.get_text(strip=True).replace("\xa0", "").replace(",", ".") for cell in cells]
            row_data[0] = convert_date(row_data[0])  
            data.append(row_data)

    df = pd.DataFrame(data, columns=headers)
    df["views"] = df["views"].str.replace(" ", "").astype(int)
    #df["Доля от всех запросов, %"] = df["Доля от всех запросов, %"].astype(float)
    df = df.drop(columns=['delete'])
    return df 

def create_driver():
    print('Создания драйвера.')
    service = Service(executable_path='driver/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Linux i556 x86_64; en-US) AppleWebKit/601.7 (KHTML, like Gecko) Chrome/51.0.1653.264 Safari/601")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless") 

    driver  = webdriver.Chrome(options=options, service=service)
    return driver

def load_cookie(driver: webdriver.Chrome):
    print('Загрузка cookie.')
    driver.get("https://wordstat.yandex.ru/")

    for cookie in pickle.load(open('driver/cookies.pkl', 'rb')):
        driver.add_cookie(cookie)

    driver.refresh()
    time.sleep(3)

def load_wordstat(mem_list: list, driver: webdriver.Chrome, year):
    full_df = pd.DataFrame(columns=['date', 'views', 'mem'])

    for mem in mem_list:
        try:
            print(f'Загрузка мема: "{mem}"')
            driver.get(f"https://wordstat.yandex.ru/?region=all&view=graph&words={mem}")
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            html_code = soup.find('table', class_='table__wrapper').prettify()

            df = extract_table_to_csv(html_code)
            df['mem'] = mem 

            driver.get(f"https://wordstat.yandex.ru/?region=all&view=table&words={mem}")
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            html_code = soup.find('td', class_='table__level-cell').getText()
            number = int(html_code.replace(' ', '')) 
            df['sum_views'] = number
            full_df = pd.concat([full_df, df])
        except:
            print("Мем никто не гуглил :(")

    full_df.to_csv(f"mem_csv/wordstat_{year}.csv", index=False)