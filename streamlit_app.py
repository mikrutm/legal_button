import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pandas as pd
import time

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        ),
        options=options,
    )
    return driver

driver = get_driver()
driver.get("https://www.gov.pl/web/premier/wplip-rm")

# Click the cookie button
try:
    cookie_button = driver.find_element("xpath", "/html/body/div[1]/div/button")
    cookie_button.click()
    time.sleep(2)  # Wait for the click action to complete and page to load
except Exception as e:
    st.write("Cookie button not found or already accepted.")

# Scrape the table
try:
    table_element = driver.find_element("xpath", "/html/body/main/div/article/div[2]/div[2]/div/table")
    table_html = table_element.get_attribute('outerHTML')
    df = pd.read_html(table_html)[0]
    st.dataframe(df)
except Exception as e:
    st.write("Table not found.")

driver.quit()
