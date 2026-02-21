import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA I STYL ---
st.set_page_config(page_title="E-Doręczenia Monitor PRO", layout="wide")

# --- 2. LOGIKA REJESTRU PRZERW (LOKALNA BAZA) ---
# Inicjalizacja listy przerw w pamięci aplikacji (tylko na tej stronie)
if 'local_events' not in st.session_state:
    st.session_state['local_events'] = []

def add_to_local_calendar(title, context):
    """Dodaje wpis do lokalnego kalendarza widocznego na stronie"""
    now = datetime.datetime.now()
    # Tworzymy unikalny klucz dla dzisiejszego wydarzenia, by nie dodawać go 100 razy
    event_id = f"{now.strftime('%Y-%m-%d')}-{title[:5]}"
    
    if not any(ev.get('id') == event_id for ev in st.session_state['local_events']):
        new_event = {
            "id": event_id,
            "title": f"❌ {title}",
            "start": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "end": (now + datetime.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%S'),
            "backgroundColor": "#FF4B4B",
            "description": context
        }
        st.session_state['local_events'].append(new_event)

# --- 3. FUNKCJE TECHNICZNE (SCRAPING, MAIL) ---
def send_full_alert(subject, context_text):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroapp.com.pl"
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Monitor Systemowy <{sender_email}>"
        msg['To'] = receiver_email
        msg.attach(MIMEText(f"Wykryto przerwę!\n\nTREŚĆ:\n{context_text}", 'plain'))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except: return False

def check_status(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Filtr eArchiwum
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

# --- 4. PASEK BOCZNY ---
with st.sidebar:
    st.title("📂 Panel Sterowania")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Oprogramowanie"])
    st.divider()
    if st.button("Czyść kalendarz przerw"):
        st.session_state['local_events'] = []
        st.rerun()

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    # --- WIDOK MIESIĘCZNY (TYLKO TUTAJ) ---
    st.subheader("📅 Kalendarz Wykrytych Przerw")
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,dayGridWeek"},
        "initialView": "dayGridMonth",
        "locale": "pl",
    }
    calendar(events=st.session_state['local_events'], options=calendar_options)
    
    st.divider()
    
    # --- STATUS STRON ---
    st.subheader("🕵️ Bieżący Status")
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
                    st.error(f"🔴 Wykryto: {', '.join(found)}")
                    st.caption(context)
                    # AUTOMATYCZNE DODANIE DO LOKALNEGO KALENDARZA
                    add_to_local_calendar(site["name"], context)
                    
                    if st.button(f"Wyślij info na maila", key=site['name']):
                        send_full_alert(f"Alert: {site['name']}", context)
                        st.success("Wysłano!")
                else:
                    st.success("🔵 System dostępny")

elif choice == "💻 System i Oprogramowanie":
    st.header("💻 Centrum Systemowe")
    col_cpu, col_disk = st.columns(2)
    with col_cpu:
        with st.container(border=True):
            st.subheader("Dell Precision 5540")
            st.write("🚀 **Procesor:** i9-9880H | 🧠 **RAM:** 32 GB")
    with col_disk:
        with st.container(border=True):
            st.subheader("Zasoby")
            st.progress(0.46, text="Dysk C: 433GB wolne")

    st.divider()
    st.subheader("⚙️ Status Oprogramowania")
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])

st.sidebar.caption(f"v2.7 | Rejestr Lokalny | eArchiwum Ignored")
