import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DYNAMICZNY KALENDARZ (AUTO-POBIERANIE Z GOV) ---
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
        content = soup.find_all(['tr', 'p', 'td'])
        for node in content:
            text = node.get_text().strip().lower()
            if "godz" in text and any(m in text for m in months):
                try:
                    day = re.search(r'(\d{1,2})', text).group(1).zfill(2)
                    month = months[next(m for m in months if m in text)]
                    year = re.search(r'(202\d)', text).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', text)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso_date = f"{year}-{month}-{day}"
                    # Unikanie duplikatów
                    if not any(e['start'] == iso_date for e in events):
                        events.append({
                            "title": f"{time_range} | GOV",
                            "start": iso_date, "end": iso_date,
                            "backgroundColor": "#EE6C4D", "display": "block", "allDay": True
                        })
                except: continue
        return events
    except: return []

# --- 3. DYNAMICZNY KOMUNIKAT POCZTY (DO CZERWONEJ LINII) ---
def get_poczta_dynamic_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Pobieramy główny blok treści
        container = soup.find('div', {'class': 'entry-content'}) or soup.find('article')
        if not container: return None

        elements = container.find_all(['p', 'h3', 'li'])
        final_text = []
        
        for el in elements:
            txt = el.get_text().strip()
            if not txt or "earchiwum" in txt.lower(): continue
            final_text.append(txt)
            # Zatrzymujemy się na dacie publikacji (koniec komunikatu)
            if re.search(r'\d{2}\.\d{2}\.\d{4}', txt):
                break
        
        return "\n\n".join(final_text) if final_text else None
    except: return "Błąd połączenia z Pocztą."

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption(f"v3.7 | Ostatnia synchronizacja: {datetime.datetime.now().strftime('%H:%M:%S')}")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        alert_pp = get_poczta_dynamic_alert()
        if alert_pp:
            st.error(alert_pp) # Dynamiczny, pełny komunikat do daty
        else:
            st.success("Brak aktywnych komunikatów.")

    with col2:
        st.subheader("🕵️ GOV.PL")
        # Wyświetlamy tylko ostatni komunikat dynamicznie
        res_gov = requests.get("https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", timeout=10)
        soup_gov = BeautifulSoup(res_gov.text, 'html.parser')
        gov_text = soup_gov.find('p').get_text() if soup_gov.find('p') else "Brak danych"
        st.warning(gov_text)

    st.divider()
    st.subheader("📅 Harmonogram (Pobierany dynamicznie)")
    calendar(events=get_dynamic_gov_
