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

    driver = get_driver()
    driver.get("https://www.gov.pl/web/premier/wplip-rm")



    def extract_table():
        # Znajdź tabelę na stronie
        table = WebDriverWait(driver, 10).until(
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
    try:
        cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'cookies-info'))
        )
        cookies_button.click()
    except Exception as e:
        print("Baner cookies nie został znaleziony lub nie można go kliknąć:", e)
    # Pobierz pierwszą tabelę
    df1 = extract_table()
    # Kliknij przycisk, aby załadować nową tabelę
    button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="js-pagination-page-next"]'))
    )
    button.click()
    # Poczekaj na załadowanie nowej tabeli
    df2 = extract_table()
    # Połącz tabele
    df_combined = pd.concat([df1, df2], ignore_index=True)
    # Zapisz wynik do pliku CSV
    df_combined.to_csv('combined_table.csv', index=False)
    # Zamknij przeglądarkę
    driver.quit()

    
    st.code(driver.page_source)
    str.echo()