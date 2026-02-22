import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v4.7
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DYNAMICZNY KALENDARZ (Z OBSŁUGĄ KLIKNIĘĆ) ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04', 'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08', 'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'}
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Pobieranie daty publikacji z tabeli (kolumna "Data publikacji")
        table = soup.find('table')
        if not table: return []
        
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                raw_dt = cols[0].get_text().strip().lower()
                podmiot = cols[1].get_text().strip()
                pub_date = cols[2].get_text().strip() # Data publikacji z 3. kolumny
                
                try:
                    day = re.search(r'(\d{1,2})', raw_dt).group(1).zfill(2)
                    month = months[next(m for m in months if m in raw_dt)]
                    year = re.search(r'(202\d)', raw_dt).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw_dt)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso_date = f"{year}-{month}-{day}"
                    event_id = f"{iso_date}_{podmiot}"
                    
                    if not any(e.get('id') == event_id for e in events):
                        events.append({
                            "id": event_id,
                            "title": f"{time_range} | {podmiot}",
                            "start": iso_date,
                            "end": iso_date,
                            "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80",
                            "display": "block",
                            "allDay": True,
                            "extendedProps": {
                                "pub_date": pub_date,
                                "provider": podmiot
                            }
                        })
                except: continue
        return events
    except: return []

# --- 3. DYNAMICZNY KOMUNIKAT POCZTY (NAPRAWIONY - v4.5) ---
def get_poczta_simple_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = []
        for p in paragraphs:
            txt = p.get_text().strip()
            if "Informujemy" in txt:
                content.append(txt)
                parent = p.find_parent()
                if parent:
                    all_p_in_parent = parent.find_all('p')
                    start_idx = all_p_in_parent.index(p)
                    for next_p in all_p_in_parent[start_idx+1:]:
                        next_txt = next_p.get_text().strip()
                        content.append(next_txt)
                        if re.fullmatch(r'\d{2}\.\d{2}\.\d{4}', next_txt): break
                break
        return "\n\n".join(content) if content else "Brak aktywnych komunikatów."
    except: return "Błąd połączenia."

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i
