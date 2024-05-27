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
import time


@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--disable-blink-features=AutomationControlled')

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
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Arkusz1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data
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
    cookie_button = WebDriverWait(driver, 12).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/button"))
    )
    cookie_button.click()
except Exception as e:
    st.write("Przycisk ciasteczek nie został znaleziony lub już zaakceptowany.")
    st.write(f"Błąd: {e}")

# Pobranie i łączenie danych z tabeli
all_data = []
st.title("DORA - Tabelka z Wykazem Prac")
#st.subheader("Narzędzie pozwalające pobrać i przeglądać tabelę z wykazem prac legislacyjnych i programowych Rady Ministrów.")
st.write("Narzędzie pozwalające pobrać i przeglądać tabelę z wykazem prac legislacyjnych i programowych Rady Ministrów. To doraźna próba naprawienia błędu na stronie https://www.gov.pl/web/premier/wplip-rm. Jeśli ta aplikacja się popsuje, jest szansa że serwis gov uznaje, że jesteśmy złośliwym botem i zblokuje ściaganie danych. Radzę wtedy po prostu poczekać chwilę, lub porposić współpracownika o tej aplikacji na swoim komputererze.")
st.write(" Tabelka się tworzy, proszę o cierpliwość.")

try:
    while True:
        # Poczekaj na załadowanie tabeli
        table_element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CLASS_NAME, "results-table"))
        )
        table_html = table_element.get_attribute('outerHTML')
        df = pd.read_html(table_html)[0]
        print(df)
        # Wyodrębnienie linków z każdej klasy "results-row"
        rows = driver.find_elements(By.CLASS_NAME, "result-row")
        print(rows)
        row_links = [row.find_element(By.TAG_NAME, "a").get_attribute('href') for row in rows]
        print(row_links)

        # Dodanie nowej kolumny z linkami do DataFrame
        df['Link'] = row_links

        all_data.append(df)

        # Próbuj kliknąć przycisk "Następna strona"
        try:
            next_button = driver.find_element(By.XPATH, '//*[@id="js-pagination-page-next"]')
            if 'disabled' in next_button.get_attribute('class'):
                break  # Wyjdź z pętli, jeśli przycisk jest nieaktywny
            next_button.click()
            time.sleep(2)  # Poczekaj na załadowanie następnej strony
        except Exception as e:
            st.write("Brak przycisku 'Następna strona' lub nieaktywny.")
            st.write(f"Błąd: {e}")
            break

    # Połącz wszystkie zebrane dane w jeden DataFrame
    
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.drop("Podgląd",axis=1,inplace=True)

    st.dataframe(final_df)
    
    final_df.to_excel('plik.xlsx', index=False,)

    st.download_button(
    label='Pobierz tabelę jako XLSX',
    data=final_df,
    file_name='plik.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


except Exception as e:
    st.write("Tabela nie została znaleziona lub nie mogła zostać załadowana.")
    st.write(f"Błąd: {e}")
st.write("Opracował: Andrzej Józefczyk")
driver.quit()
