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
import random
import socket

st.title("DORA - Wykaz Prac")
st.write("Narzędzie pozwalające pobrać i przeglądać tabelę z wykazem prac legislacyjnych i programowych Rady Ministrów. Jest to doraźna próba naprawienia błędu na stronie https://www.gov.pl/web/premier/wplip-rm. Jeśli ta aplikacja się popsuje, jest szansa że serwis gov uznaje, że jesteśmy złośliwym botem i zblokuje ściaganie danych. Radzę wtedy po prostu poczekać chwilę, lub porposić współpracownika o odpalenie tej aplikacji na swoim komputererze.")

def find_free_port():
    while True:
        port = random.randint(1024, 65535)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                print(port)
                return port
            
def is_host_free(host):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, 80)) != 0

# Funkcja do znalezienia wolnego hosta w danym zakresie
def find_free_host():
    base_ip = '192.168.0.'
    for i in range(2, 255):
        host = f"{base_ip}{i}"
        if is_host_free(host):
            print(host)
            return host
    raise RuntimeError("Nie znaleziono wolnych hostów w podanym zakresie.")

port = find_free_port() 

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Arkusz1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data
# Inicjalizacja WebDriver

@st.cache_resource


def get_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--remote-debugging-port={port}")
    #options.add_argument(f'--host={host}')
    
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

try:
    driver = get_driver()
    #driver.get("https://www.topagrar.pl/articles/aktualnosci/protest-rolnikow-ke-odroczy-chwilowo-wymogi-przed-wyborami-do-pe-a-co-potem-2511126")
    driver.get("https://www.gov.pl/web/premier/wplip-rm")
except Exception as e:
    st.error(f"Błąd podczas łączenia się z ChromeDriver: {e}")
    driver.quit()
    st.stop()


if st.button("Stwórz tabelę "):
    st.write(" Tabelka się tworzy, proszę o cierpliwość.")

    #host = find_free_host()
    


# Kliknięcie przycisku ciasteczek
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/button"))
        )
        cookie_button.click()
    except Exception as e:
        st.write("Przycisk ciasteczek nie został znaleziony lub już zaakceptowany.")
        st.write(f"{e}")

    try:
        c_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/article/div[2]/div[2]/nav/div[2]/div/a[3]"))
        )
        c_button.click()
    except Exception as e:
        st.write("Przycisk ciasteczek nie został znaleziony lub już zaakceptowany.")
        st.write(f"Błąd: {e}")


    all_data = []

    try:
        while True:
            # Poczekaj na załadowanie tabeli
            table_element = WebDriverWait(driver, 3).until(
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
        #driver.quit()    
        
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.drop("Podgląd",axis=1,inplace=True)

        st.dataframe(final_df)
        import io
      # Konwertuj DataFrame do formatu Excel i zapisz w pamięci
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False)

        # Przejdź do początku bufora
        excel_buffer.seek(0)

        # Dodaj przycisk do pobrania pliku
        st.download_button(
            label="Pobierz plik XLSX",
            data=excel_buffer,
            file_name="downloaded_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreads")


    except Exception as e:
        st.write("Tabela nie została znaleziona lub nie mogła zostać załadowana.")
        st.write(f"Błąd: {e}")
    st.write("Opracował: Andrzej Józefczyk")