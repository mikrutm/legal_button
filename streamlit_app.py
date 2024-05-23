import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pandas as pd
from bs4 import BeautifulSoup

"""
## Web scraping on Streamlit Cloud with Selenium

[![Source](https://img.shields.io/badge/View-Source-<COLOR>.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)

This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.

Fork this repo, and edit `/streamlit_app.py` to customize this app to your heart's desire. :heart:
"""

@st.cache(allow_output_mutation=True)
def get_driver():        
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        ),
        options=options,
    )

def extract_table_to_df(url):
    driver = get_driver()
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table')
    if table is None:
        st.write("Nie znaleziono tabeli na stronie.")
        return None
    else:
        return pd.read_html(str(table))[0]

# Przykładowe użycie funkcji
url = "https://www.gov.pl/web/premier/wplip-rm"  # Zastąp 'http://example.com' adresem twojej strony
df = extract_table_to_df(url)
if df is not None:
    st.write("Tabela ze strony:")
    st.write(df)
