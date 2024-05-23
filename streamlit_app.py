import streamlit as st
import pandas as pd    
with st.echo():

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait 
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

    @st.cache_resource
    def get_driver():
        return webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')  # Add this option if running on Linux
    options.add_argument('--disable-dev-shm-usage')  # Add this option if running on Linux
    
    driver = get_driver()
    driver.get("https://www.gov.pl/web/premier/wplip-rm")



def extract_table():
    try:
        # Znajdź tabelę na stronie
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )

        # Pobierz wszystkie wiersze i komórki z tabeli
        rows = table.find_elements(By.TAG_NAME, 'tr')
        table_data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            cols = [col.text for col in cols]
            table_data.append(cols)
        
        return pd.DataFrame(table_data)
    except TimeoutException as e:
        print("Nie znaleziono tabeli w określonym czasie.")
        raise e

    # Zamknij baner cookies, jeśli jest obecny
try:
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'cookies-info'))
    )
    cookies_button.click()
    print("Baner cookies zamknięty.")
except TimeoutException:
    print("Baner cookies nie został znaleziony lub nie można go kliknąć.")
except Exception as e:
    print("Inny błąd podczas zamykania banera cookies:", e)

# Poczekaj na zniknięcie banera cookies
try:
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, 'cookies-info'))
    )
    print("Baner cookies zniknął.")
except TimeoutException:
    print("Baner cookies nadal widoczny po 10 sekundach.")
    driver.quit()
    raise

# Pobierz pierwszą tabelę
try:
    df1 = extract_table()
    print("Pierwsza tabela pobrana pomyślnie.")
except TimeoutException as e:
    print("Nie udało się pobrać pierwszej tabeli.")
    driver.quit()
    raise e

# Kliknij przycisk, aby załadować nową tabelę
try:
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'js-pagination-page-next'))
    )
    button.click()
    print("Przycisk do załadowania nowej tabeli został kliknięty.")
except ElementClickInterceptedException:
    print("Przycisk do załadowania nowej tabeli został zasłonięty. Próbuję ponownie po zamknięciu banera.")
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'cookies-info'))
    )
    cookies_button.click()
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, 'cookies-info'))
    )
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'js-pagination-page-next'))
    )
    button.click()
    print("Przycisk do załadowania nowej tabeli został kliknięty.")
except TimeoutException as e:
    print("Nie udało się kliknąć przycisku do załadowania nowej tabeli.")
    driver.quit()
    raise e

# Poczekaj na załadowanie nowej tabeli
try:
    df2 = extract_table()
    print("Nowa tabela pobrana pomyślnie.")
except TimeoutException as e:
    print("Nie udało się pobrać nowej tabeli.")
    driver.quit()
    raise e

# Połącz tabele
df_combined = pd.concat([df1, df2], ignore_index=True)

# Zapisz wynik do pliku CSV
df_combined.to_csv('combined_table.csv', index=False)
print("Tabele połączone i zapisane do pliku CSV.")


st.code(driver.page_source)
str.echo()