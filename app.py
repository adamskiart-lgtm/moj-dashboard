import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DYNAMICZNY KALENDARZ (POBIERANIE DANYCH Z TABELI GOV) ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {
        'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
        'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
        'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
    }
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Szukamy tabeli na stronie
        table = soup.find('table')
        if not table: return []
        
        rows = table.find_all('tr')[1:] # Pomijamy nagłówek
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                # Kolumna 0: Data i godzina
                raw_datetime = cols[0].get_text().strip().lower()
                # Kolumna 1: Podmiot realizujący prace
                podmiot = cols[1].get_text().strip()
                
                try:
                    # Wyciąganie daty (RRRR-MM-DD)
                    day = re.search(r'(\d{1,2})', raw_datetime).group(1).zfill(2)
                    month_name = next(m for m in months if m in raw_datetime)
                    month = months[month_name]
                    year_match = re.search(r'(202\d)', raw_datetime)
                    year = year_match.group(1) if year_match else str(datetime.datetime.now().year)
                    
                    # Wyciąganie godzin
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw_datetime)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    
                    iso_date = f"{year}-{month}-{day}"
                    
                    # UNIKANIE DUBLOWANIA: identyfikacja po dacie i podmiocie
                    event_id = f"{iso_date}_{podmiot}"
                    if not any(e.get('id') == event_id for e in events):
                        events.append({
                            "id": event_id,
                            "title": f"{time_range} | Zgłosił: {podmiot}",
                            "start": iso_date,
                            "end": iso_date,
                            "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80",
                            "display": "block",
                            "allDay": True
                        })
                except: continue
        return events
    except: return []

# --- 3. POBIERANIE KOMUNIKATÓW ---
def get_poczta_dynamic_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        container = soup.find('div', {'class': 'entry-content'}) or soup.find('article')
        if not container: return None
        elements = container.find_all(['p', 'h3', 'li'])
        final_text = []
        for el in elements:
            txt = el.get_text().strip()
            if not txt or "earchiwum" in txt.lower(): continue
            final_text.append(txt)
            if re.search(r'\d{2}\.\d{2}\.\d{4}', txt): break
        return "\n\n".join(final_text) if final_text else None
    except: return "Błąd połączenia."

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.write("**Wersja kodu:** v4.0")
    st.caption(f"Aktualizacja: {datetime.datetime.now().strftime('%H:%M:%S')}")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        alert_pp = get_poczta_dynamic_alert()
        if alert_pp:
            st.error(alert_pp)
        st.link_button("Otwórz stronę Poczty ➔", "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/")

    with col2:
        st.subheader("🕵️ GOV.PL")
        # Pobieranie pierwszego akapitu z tabeli/strony jako komunikat
        st.info("Dane pobierane bezpośrednio z tabeli niedostępności GOV.PL.")
        st.link_button("Otwórz stronę GOV ➔", "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen")

    st.divider()
    st.subheader("📅 Harmonogram (Dane z tabeli GOV.PL)")
    calendar(events=get_dynamic_gov_events(), options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False
    })

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Dell Precision 5540 | i9 | 32GB RAM")
    st.table([{"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"}, {"Program": "Microsoft Edge", "Status": "✅ OK"}])
