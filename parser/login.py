import time 
import json 
import pickle
import codecs

from selenium import webdriver
from selenium.webdriver.common.by import By

def login(driver):
    time.sleep(5)
    email_input = driver.find_element(by=By.ID, value="passp-field-login")
    email_input.clear()
    email_input.send_keys(name)

    driver.find_element(by=By.ID, value="passp:sign-in").click()
    time.sleep(2)

    password_input = driver.find_element(by=By.ID, value="passp-field-passwd")
    password_input.clear()
    password_input.send_keys(password)
    driver.find_element(by=By.ID, value="passp:sign-in").click()

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Linux; Linux i556 x86_64; en-US) AppleWebKit/601.7 (KHTML, like Gecko) Chrome/51.0.1653.264 Safari/601")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-Advertisement")
options.add_argument("--disable-popup-blocking") 
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled") 

name = "Ваше имя"
password = "Ваш пароль"
url = "https://passport.yandex.ru/auth/add/login"

driver  = webdriver.Chrome(options=options)
driver.get(url)
login(driver) 

time.sleep(5)
driver.get("https://wordstat.yandex.ru/")
time.sleep(5)
pickle.dump( driver.get_cookies() , open("driver/cookies.pkl","wb"))
driver.quit()
