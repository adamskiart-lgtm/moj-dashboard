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

# --- 3. ZMODYFIKOWANA FUNKCJA SCRAPUJĄCA (TYLKO PRZERWY, BEZ MENU) ---
def get_clean_alerts(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Usuwamy eArchiwum oraz typowe elementy menu/nav
        for tag in soup(['nav', 'header', 'footer', 'script', 'style', 'button', 'form']):
            tag.extract()

        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()
            
        # Szukamy tylko w paragrafach i listach, gdzie tekst jest dłuższy (komunikaty)
        potential_nodes = soup.find_all(['p', 'li', 'div'])
        alerts = []
        
        for node in potential_nodes:
            # Pobieramy tekst bez dzieci, żeby nie powtarzać zagnieżdżonych divów
            text = node.get_text(" ", strip=True)
            
            # Warunki: zawiera słowo kluczowe ORAZ jest wystarczająco długi (pomija menu)
            if any(word in text.lower() for word in keywords) and len(text) > 40:
                if text not in alerts:
                    # Dodatkowe czyszczenie z wielokrotnych spacji
                    clean_text = re.sub(r'\s+', ' ', text)
                    alerts.append(clean_text)
        
        if not alerts:
            return None, []
        
        # Zwracamy najnowszy (pierwszy) i resztę jako archiwum
        return alerts[0], alerts[1:]
    except Exception as e:
        return f"Błąd połączenia: {e}", []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption("v3.1 | Clean Polish Post Alerts")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    sites = [
        {"name": "Poczta Polska (Prace Serwisowe)", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["przerwa", "techniczna", "utrudnienia", "awaria"]},
        {"name": "GOV.PL (Status Usługi)", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "planowana", "przerwa"]}
    ]

    for site in sites:
        latest, archive = get_clean_alerts(site["url"], site["keywords"])
        
        with st.container(border=True):
            st.subheader(f"🕵️ {site['name']}")
            if latest:
                st.error("**OSTATNI KOMUNIKAT:**")
                st.write(latest)
                
                if archive:
                    with st.expander("📁 Starsze wpisy z tej strony"):
                        for msg in archive:
                            st.write(f"• {msg}")
                            st.divider()
            else:
                st.success("✅ Brak aktywnych informacji o przerwach.")

    st.divider()

    # KALENDARZ NA DOLE
    st.subheader("📅 Harmonogram Planowany (Historyczny)")
    all_events = get_gov_planned_events()
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth",
        "height": 480,
        "locale": "pl"
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
