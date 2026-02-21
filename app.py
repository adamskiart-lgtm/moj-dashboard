import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DANE Z TWOJEJ TABELI (KALENDARZ) ---
def get_gov_planned_events():
    raw_data = [
        ("2026-03-01", "15:00", "20:00", "PPSA"),
        ("2026-02-26", "18:00", "23:00", "PPSA"),
        ("2026-02-18", "18:00", "23:00", "PPSA"),
        ("2026-02-15", "15:00", "20:00", "PPSA"),
        ("2026-02-08", "15:00", "20:00", "PPSA"),
        ("2026-02-03", "12:50", "14:00", "COI"),
        ("2026-02-01", "15:00", "20:00", "PPSA"),
        ("2026-01-30", "22:00", "02:00", "COI"),
    ]
    events = []
    for d, s, e, p in raw_data:
        events.append({
            "title": f"{s}-{e} | {p}",
            "start": f"{d}T{s}:00",
            "end": f"{d}T{e}:00",
            "backgroundColor": "#EE6C4D",
            "display": "block"
        })
    return events

# --- 3. FUNKCJA POBIERANIA KOMUNIKATÓW (TYLKO OSTATNI) ---
def get_alerts_split(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()
            
        text_nodes = soup.find_all(['p', 'div', 'li'])
        alerts = []
        
        for node in text_nodes:
            node_text = node.get_text().strip()
            if any(word in node_text.lower() for word in keywords) and len(node_text) > 10:
                if node_text not in alerts:
                    alerts.append(node_text)
        
        if not alerts:
            return None, []
        
        # Zwracamy: (Najnowszy, Reszta)
        return alerts[0], alerts[1:]
    except:
        return "Błąd połączenia.", []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption("v3.0 | Focus: Latest Alert Only")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    sites = [
        {"name": "Poczta Polska (Prace Serwisowe)", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["awaria", "techniczna", "utrudnienia"]},
        {"name": "GOV.PL (Status Usługi)", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "planowana", "przerwa"]}
    ]

    for site in sites:
        latest, archive = get_alerts_split(site["url"], site["keywords"])
        
        st.subheader(f"🕵️ {site['name']}")
        if latest:
            st.error("**NAJNOWSZY KOMUNIKAT:**")
            st.write(latest)
            
            if archive:
                with st.expander("📁 Zobacz pozostałe (starsze) komunikaty"):
                    for msg in archive:
                        st.write(f"• {msg}")
                        st.divider()
        else:
            st.success("✅ Brak aktywnych alertów")

    st.divider()

    # KALENDARZ NA DOLE
    st.subheader("📅 Planowane przerwy")
    all_events = get_gov_planned_events()
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth",
        "height": 480,
        "locale": "pl",
        "displayEventTime": True
    }
    calendar(events=all_events, options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Dell Precision 5540 | i9 | 32GB RAM")
    st.progress(0.46, text="Dysk C: 433GB wolne")
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])
