import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. KALENDARZ (KOD ZAMROŻONY - BEZ ZMIAN) ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04', 'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08', 'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'}
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table: return []
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                raw_dt = cols[0].get_text().strip().lower()
                podmiot = cols[1].get_text().strip()
                try:
                    day = re.search(r'(\d{1,2})', raw_dt).group(1).zfill(2)
                    month = months[next(m for m in months if m in raw_dt)]
                    year = re.search(r'(202\d)', raw_dt).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw_dt)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso_date = f"{year}-{month}-{day}"
                    event_id = f"{iso_date}_{podmiot}"
                    if not any(e.get('id') == event_id for e in events):
                        events.append({"id": event_id, "title": f"{time_range} | Zgłosił: {podmiot}", "start": iso_date, "end": iso_date, "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80", "display": "block", "allDay": True})
                except: continue
        return events
    except: return []

# --- 3. PRECYZYJNE POBIERANIE KOMUNIKATU (OD NAGŁÓWKA DO DATY) ---
def get_poczta_clean_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Szukamy kontenera z treścią
        container = soup.find('div', {'class': 'entry-content'}) or soup.find('article')
        if not container: return "Nie znaleziono treści komunikatu."

        # Pobieramy elementy tekstowe
        elements = container.find_all(['p', 'h3', 'li'])
        content_parts = []
        
        for el in elements:
            txt = el.get_text().strip()
            if not txt or "Prace serwisowe" in txt: continue # Pomijamy nagłówek startowy
            
            content_parts.append(txt)
            
            # ZATRZYMANIE: Szukamy daty publikacji (np. 20.02.2026), która kończy komunikat nad linią
            if re.search(r'\d{2}\.\d{2}\.\d{4}', txt):
                break
        
        return "\n\n".join(content_parts) if content_parts else "Brak nowych komunikatów."
    except:
        return "Błąd połączenia ze stroną Poczty Polskiej."

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.write("**Wersja kodu:** v4.1")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    
    col1, col2 = st.columns(2)
    
    # SEKCJA POCZTA POLSKA
    with col1:
        st.subheader("🕵️ Poczta Polska")
        # Wyświetlenie komunikatu (od "Informujemy..." do daty publikacji)
        alert_text = get_poczta_clean_alert()
        st.info(alert_text)
        
        # Link jako niebieska nazwa
        st.markdown('[Strona Poczty Polskiej - Prace serwisowe](https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/)')

    # SEKCJA GOV.PL
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.write("Ostatnie ogłoszenia o planowanych przerwach technicznych dostępne w tabeli poniżej.")
        
        # Link jako niebieska nazwa
        st.markdown('[Strona GOV.PL - Niedostępność e-Doręczeń](https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen)')

    st.divider()
    
    # KALENDARZ (ZAMROŻONY)
    st.subheader("📅 Harmonogram (Zgłoszenia PP / COI)")
    calendar(events=get_dynamic_gov_events(), options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False
    })

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.table([{"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"}, {"Program": "Microsoft Edge", "Status": "✅ OK"}])
