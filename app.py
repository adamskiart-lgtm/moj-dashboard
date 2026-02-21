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

# --- 2. DANE Z TABELI GOV (ZGODNIE Z TWOIM WYKAZEM) ---
def get_gov_planned_events():
    """Przetwarza dane na format kalendarza z widocznymi godzinami"""
    # Format: (Data, Godzina_Start, Godzina_End, Opis)
    raw_data = [
        ("2026-03-01", "15:00", "20:00", "PPSA"),
        ("2026-02-26", "18:00", "23:00", "PPSA"),
        ("2026-02-18", "18:00", "23:00", "PPSA"),
        ("2026-02-15", "15:00", "20:00", "PPSA"),
        ("2026-02-08", "15:00", "20:00", "PPSA"),
        ("2026-02-03", "12:50", "14:00", "COI"),
        ("2026-02-01", "15:00", "20:00", "PPSA"),
        ("2026-01-30", "22:00", "02:00", "COI (Noc 30/31)"),
        ("2026-01-15", "18:00", "23:00", "PP S.A."),
    ]
    
    events = []
    for d, s, e, p in raw_data:
        # Dodajemy godziny do tytułu, aby były widoczne bez najeżdżania myszką
        events.append({
            "title": f"{s}-{e} | {p}",
            "start": f"{d}T{s}:00",
            "end": f"{d}T{e}:00",
            "backgroundColor": "#EE6C4D",
            "display": "block" # Wymusza renderowanie paska z tekstem
        })
    return events

# --- 3. FUNKCJA POBIERANIA PEŁNEJ TREŚCI KOMUNIKATU ---
def get_full_alert_content(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Filtr eArchiwum
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()
            
        # Szukamy głównego tekstu komunikatu
        # Na GOV.PL i Poczcie komunikaty są zazwyczaj w artykułach lub divach o klasie 'editor-content'
        content_found = ""
        text_nodes = soup.find_all(['p', 'div', 'li'])
        
        for node in text_nodes:
            node_text = node.get_text().strip()
            if any(word in node_text.lower() for word in keywords):
                # Jeśli znajdziemy słowo kluczowe, bierzemy tekst rodzica, by mieć pełny kontekst akapitu
                content_found += node_text + "\n\n"
        
        return content_found if content_found else None
    except:
        return "Błąd połączenia ze stroną."

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption("v2.9 | artur.adamski@agroapp.com.pl")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    # PEŁNE KOMUNIKATY (Zawsze pełna treść)
    st.subheader("🕵️ Bieżące Komunikaty Operacyjne")
    
    sites = [
        {"name": "Poczta Polska (Prace Serwisowe)", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["awaria", "techniczna", "utrudnienia"]},
        {"name": "GOV.PL (Status Usługi)", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "planowana", "przerwa"]}
    ]

    for site in sites:
        full_msg = get_full_alert_content(site["url"], site["keywords"])
        with st.expander(f"Źródło: {site['name']}", expanded=True):
            if full_msg:
                st.error(f"⚠️ WYKRYTO KOMUNIKAT:")
                st.write(full_msg) # Tutaj wyświetla się pełna treść
            else:
                st.success(f"✅ Brak aktywnych alertów dla {site['name']}")

    st.divider()

    # KALENDARZ NA DOLE (Z widocznymi godzinami)
    st.subheader("📅 Planowane przerwy (Widok kalendarza)")
    
    all_events = get_gov_planned_events()
    
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth",
        "height": 500,
        "locale": "pl",
        "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "meridiem": False, "hour12": False},
        "dayMaxEvents": True
    }
    
    calendar(events=all_events, options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Specyfikacja: Dell Precision 5540 | i9 | 32GB RAM")
    st.progress(0.46, text="Dysk C: 433GB wolne")
    st.divider()
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])
