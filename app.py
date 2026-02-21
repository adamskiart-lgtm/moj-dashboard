import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DYNAMICZNY KALENDARZ (AUTO-PARSER) ---
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
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Brak godz."
                    iso_date = f"{year}-{month}-{day}"
                    events.append({
                        "title": f"{time_range} | GOV",
                        "start": iso_date, "end": iso_date,
                        "backgroundColor": "#EE6C4D", "display": "block", "allDay": True
                    })
                except: continue
        return events
    except: return []

# --- 3. PRECYZYJNE POBIERANIE OSTATNIEGO KOMUNIKATU ---
def get_poczta_strict_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Wycinamy zbędne sekcje eArchiwum i menu
        for t in soup(['nav', 'header', 'footer', 'script', 'style', 'button']): t.extract()
        
        # Szukamy głównego bloku treści
        container = soup.find('div', {'class': 'entry-content'}) or soup.find('article')
        if not container: return None

        # Pobieramy elementy wewnątrz kontenera (akapity, nagłówki)
        elements = container.find_all(['p', 'h3', 'h4', 'h2', 'li'])
        final_text = []
        
        for el in elements:
            txt = el.get_text().strip()
            if "earchiwum" in txt.lower(): continue
            if not txt: continue
            
            final_text.append(txt)
            
            # KLUCZOWY MOMENT: Jeśli linia zawiera datę (koniec komunikatu przed czerwoną linią), STOP.
            if re.search(r'\d{2}\.\d{2}\.\d{4}', txt):
                break
        
        return "\n\n".join(final_text) if final_text else None
    except: return "Błąd połączenia z Pocztą."

def get_gov_latest_alert():
    try:
        url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        nodes = soup.find_all(['p', 'div'])
        for node in nodes:
            txt = node.get_text().strip()
            if any(w in txt.lower() for w in ["niedostępność", "planowana", "przerwa"]) and len(txt) > 80:
                return txt
        return None
    except: return "Błąd połączenia z GOV."

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption(f"v3.6 | Red Line Protection\n{datetime.datetime.now().strftime('%H:%M:%S')}")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        alert_pp = get_poczta_strict_alert()
        if alert_pp:
            st.error(alert_pp)
        else:
            st.success("Brak aktywnych komunikatów.")

    with col2:
        st.subheader("🕵️ GOV.PL")
        alert_gov = get_gov_latest_alert()
        if alert_gov:
            st.warning(alert_gov)
        else:
            st.success("Brak aktywnych komunikatów.")

    st.divider()
    st.subheader("📅 Harmonogram Planowany (Pobierany z GOV)")
    calendar(events=get_dynamic_gov_events(), options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False
    })

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Dell Precision 5540 | i9 | 32GB RAM")
    st.table([{"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"}, {"Program": "Microsoft Edge", "Status": "✅ OK"}])
