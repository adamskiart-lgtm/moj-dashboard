import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v3.8
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DYNAMICZNY KALENDARZ (AUTO-POBIERANIE Z GOV.PL) ---
def get_dynamic_gov_events():
    """
    Automatycznie pobiera tabelę przerw z GOV.PL i konwertuje ją na format kalendarza.
    Eliminuje duplikaty i systemowe wytłuszczenia godzin.
    """
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
        # Przeszukiwanie wierszy tabeli i paragrafów
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
                    
                    # Unikanie duplikatów w widoku
                    if not any(e['start'] == iso_date for e in events):
                        events.append({
                            "title": f"{time_range} | GOV",
                            "start": iso_date,
                            "end": iso_date,
                            "backgroundColor": "#EE6C4D",
                            "display": "block",
                            "allDay": True # Usuwa domyślne godziny systemowe
                        })
                except: continue
        return events
    except: return []

# --- 3. PRECYZYJNE POBIERANIE KOMUNIKATÓW (POCZTA DO LINII, GOV PEŁNY) ---
def get_poczta_dynamic_alert():
    """
    Pobiera ostatni komunikat z Poczty Polskiej. 
    Zatrzymuje się na dacie publikacji (czerwona linia na stronie).
    """
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
            # Przerwanie po napotkaniu daty (koniec bloku komunikatu)
            if re.search(r'\d{2}\.\d{2}\.\d{4}', txt):
                break
        return "\n\n".join(final_text) if final_text else None
    except: return "Błąd połączenia z serwerem Poczty."

def get_gov_latest_alert():
    """Pobiera pełną treść najnowszego komunikatu z GOV.PL"""
    try:
        url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Szukamy pierwszego merytorycznego akapitu z informacją
        nodes = soup.find_all(['p', 'div'])
        for node in nodes:
            txt = node.get_text().strip()
            if any(w in txt.lower() for w in ["niedostępność", "planowana", "przerwa"]) and len(txt) > 60:
                return txt
        return None
    except: return "Błąd połączenia z serwerem GOV."

# --- 4. INTERFEJS UŻYTKOWNIKA ---
with st.sidebar:
    st.title("📂 Menu Dashboardu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.write(f"**Wersja kodu:** v3.8")
    st.caption(f"Ostatnie odświeżenie: {datetime.datetime.now().strftime('%H:%M:%S')}")
    st.divider()
    st.caption("artur.adamski@agroapp.com.pl")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń (Status Live)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska (Ostatni)")
        alert_pp = get_poczta_dynamic_alert()
        if alert_pp:
            st.error(alert_pp)
        else:
            st.success("Brak aktywnych alertów na stronie Poczty.")

    with col2:
        st.subheader("🕵️ GOV.PL (Ostatni)")
        alert_gov = get_gov_latest_alert()
        if alert_gov:
            st.warning(alert_gov)
        else:
            st.success("Brak aktywnych alertów na stronie GOV.")

    st.divider()
    st.subheader("📅 Harmonogram Przerw (Dynamiczny)")
    # Kalendarz pobierający dane automatycznie
    calendar(events=get_dynamic_gov_events(), options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth", 
        "height": 450, 
        "locale": "pl", 
        "displayEventTime": False
    })

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Dell Precision 5540 | i9 | 32GB RAM")
    
    c1, c2 = st.columns(2)
    c1.metric("Dysk C:", "433 GB Wolne", "OK")
    c2.metric("Stabilność", "100%", "Live")
    
    st.divider()
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Status": "⚠️ Update"}
    ])
