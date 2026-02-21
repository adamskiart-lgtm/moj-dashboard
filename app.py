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

# --- 2. DANE HISTORYCZNE I PLANOWANE (Z TWOJEJ TABELI) ---
def get_gov_planned_events():
    """Przetwarza dane z tabeli GOV na format kalendarza"""
    planned_data = [
        ("2026-03-01", "15:00", "20:00", "PPSA"),
        ("2026-02-26", "18:00", "23:00", "PPSA"),
        ("2026-02-18", "18:00", "23:00", "PPSA"),
        ("2026-02-15", "15:00", "20:00", "PPSA"),
        ("2026-02-08", "15:00", "20:00", "PPSA"),
        ("2026-02-01", "15:00", "20:00", "PPSA"),
        # Możesz tu dopisać kolejne daty z listy w formacie YYYY-MM-DD
    ]
    
    events = []
    for date, start_t, end_t, provider in planned_data:
        events.append({
            "title": f"🕒 Planowana: {provider}",
            "start": f"{date}T{start_t}:00",
            "end": f"{date}T{end_t}:00",
            "backgroundColor": "#FFA500", # Pomarańczowy dla planowanych
            "borderColor": "#CC8400"
        })
    return events

# --- 3. FUNKCJE MONITORINGU ---
def check_status(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()
        full_text = soup.get_text()
        text_l = full_text.lower()
        found = [w for w in keywords if w in text_l]
        context = ""
        if found:
            idx = text_l.find(found[0])
            context = full_text[max(0, idx-40):min(len(full_text), idx+180)].strip()
        return found, context
    except: return None, ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Panel")
    choice = st.radio("Menu:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption(f"v2.8 | Artur Adamski")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    # GÓRA: Aktualny status
    col1, col2 = st.columns(2)
    sites = [
        {"name": "Poczta Polska", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["przerwa", "techniczna", "utrudnienia"]},
        {"name": "GOV.PL", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "awaria", "przerwa"]}
    ]

    for i, site in enumerate(sites):
        found, context = check_status(site["url"], site["keywords"])
        with [col1, col2][i]:
            with st.container(border=True):
                st.subheader(site["name"])
                if found:
                    st.error(f"🔴 Wykryto utrudnienia!")
                    st.write(f"_{context}_")
                else:
                    st.success("🔵 Brak bieżących komunikatów")

    st.divider()

    # DÓŁ: Kalendarz (Mniejszy)
    st.subheader("📅 Harmonogram Niedostępności (Historyczne i Planowane)")
    
    # Łączymy wydarzenia wykryte w sesji z tymi z tabeli GOV
    if 'session_alerts' not in st.session_state:
        st.session_state['session_alerts'] = []
    
    all_calendar_events = get_gov_planned_events() + st.session_state['session_alerts']

    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth",
        "height": 450, # Zmniejszona wysokość kalendarza
        "locale": "pl",
        "buttonText": {"today": "Dziś", "month": "Miesiąc", "list": "Lista"}
    }
    
    calendar(events=all_calendar_events, options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.subheader("Dell Precision 5540 | i9 | 32GB RAM")
    st.progress(0.46, text="Dysk C: 433GB wolne")
    st.divider()
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])
