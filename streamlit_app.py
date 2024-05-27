import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")  # Ustawienie portu zdalnego debugowania

    try:
        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )
    except Exception as e:
        st.error(f"Błąd podczas inicjalizacji ChromeDriver: {e}")
        raise
    return driver

# Inicjalizacja WebDriver
try:
    driver = get_driver()
    driver.get("https://www.gov.pl/web/premier/wplip-rm")
except Exception as e:
    st.error(f"Błąd podczas łączenia się z ChromeDriver: {e}")
    driver.quit()
    st.stop()

# Kliknięcie przycisku ciasteczek
try:
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/button"))
    )
    cookie_button.click()
except Exception as e:
    st.write("Przycisk ciasteczek nie został znaleziony lub już zaakceptowany.")
    st.write(f"Błąd: {e}")

# Pobranie tabeli
try:
    table_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "results-table"))
    )
    table_html = table_element.get_attribute('outerHTML')
    df = pd.read_html(table_html)[0]
    st.dataframe(df)
except Exception as e:
    st.write("Tabela nie została znaleziona lub nie mogła zostać załadowana.")
    st.write(f"Błąd: {e}")

driver.quit()
