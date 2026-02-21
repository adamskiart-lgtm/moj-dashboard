import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DANE DO KALENDARZA (BEZ DUBELTOWYCH GODZIN) ---
def get_gov_planned_events():
    # Uproszczona lista - godziny podajemy TYLKO w tytule
    raw_data = [
        ("2026-03-01", "15:00-20:00", "PPSA"),
        ("2026-02-26", "18:00-23:00", "PPSA"),
        ("2026-02-18", "18:00-23:00", "PPSA"),
        ("2026-02-15", "15:00-20:00", "PPSA"),
        ("2026-02-08", "15:00-20:00", "PPSA"),
    ]
    events = []
    for d, time_range, p in raw_data:
        events.append({
            "title": f"{time_range} | {p}",
            "start": d, # Podajemy tylko datę, by uniknąć dublowania godzin przez system kalendarza
            "end": d,
            "backgroundColor": "#EE6C4D",
            "display": "block",
            "allDay": True # Dzięki temu godzina z systemu nie dopisuje się obok Twojego tytułu
        })
    return events

# --- 3. UNIWERSALNA FUNKCJA POBIERANIA OSTATNIEGO KOMUNIKATU ---
def get_latest_alert(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Czyszczenie śmieci
        for t in soup(['nav', 'header', 'footer', 'script', 'style', 'button']):
            t.extract()
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()

        # Pobieranie tekstów i szukanie pierwszego pasującego bloku
        nodes = soup.find_all(['p', 'div', 'li', 'article'])
        for node in nodes:
            text = node.get_text(" ", strip=True)
            if any(w in text.lower() for w in keywords) and len(text) > 50:
                # Jeśli to Poczta Polska, tniemy po dacie publikacji (do czerwonej linii)
                date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
                if date_match:
                    return text[:date_match.end()]
                return text
        return None
    except:
        return "Błąd połączenia."

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption("v3.3 | Final Version")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Ostatnie Komunikaty e-Doręczeń")
    
    col1, col2 = st.columns(2)
    
    # Źródło 1: Poczta Polska
    with col1:
        st.subheader("🕵️ Poczta Polska")
        alert_pp = get_latest_alert("https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", ["przerwa", "techniczna", "awaria"])
        if alert_pp:
            st.error(alert_pp)
        else:
            st.success("Brak nowych komunikatów.")

    # Źródło 2: GOV.PL
    with col2:
        st.subheader("🕵️ GOV.PL")
        alert_gov = get_latest_alert("https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", ["niedostępność", "planowana", "przerwa"])
        if alert_gov:
            st.warning(alert_gov)
        else:
            st.success("Brak nowych komunikatów.")

    st.divider()

    # KALENDARZ NA DOLE (WYCZYSZCZONY)
    st.subheader("📅 Harmonogram Planowany")
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth",
        "height": 450,
        "locale": "pl",
        "displayEventTime": False # TO USUWA WYTEŁUSZCZONE GODZINY SYSTEMOWE
    }
    calendar(events=get_gov_planned_events(), options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.write("Dell Precision 5540 | i9 | 32GB RAM")
    st.progress(0.46, text="Dysk C: 433GB wolne")
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])
