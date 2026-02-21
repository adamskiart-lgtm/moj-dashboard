import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="E-Doręczenia Monitor", layout="wide")

# --- FUNKCJA WYSYŁANIA MAILA ---
def send_email_alert(subject, message):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroap.com.pl"

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = f"Monitor Dashboard <{sender_email}>"
        msg['To'] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        return f"Błąd: {str(e)}"

# --- FUNKCJA MONITOROWANIA ---
def check_service_status(url, keywords):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        found = [word for word in keywords if word in text]
        return found if found else None
    except:
        return "Błąd połączenia"

# --- UKŁAD STRONY ---
st.title("📡 Monitor Usług E-Doręczeń")
st.write(f"Ostatnie sprawdzenie: **{datetime.datetime.now().strftime('%H:%M:%S')}**")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("🕵️ Status Monitorowania Stron")
    
    sites = [
        {"name": "Poczta Polska - Serwis", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["przerwa", "techniczna", "utrudnienia"]},
        {"name": "GOV.PL - Niedostępność", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "awaria", "przerwa"]}
    ]

    any_alert = False
    for site in sites:
        status = check_service_status(site["url"], site["keywords"])
        with st.expander(f"🌐 {site['name']}", expanded=True):
            if isinstance(status, list):
                st.error(f"⚠️ Wykryto wzmianki o przerwach: {', '.join(status)}")
                any_alert = True
            elif status == "Błąd połączenia":
                st.warning("Nie udało się połączyć ze stroną.")
            else:
                st.success("✅ Brak informacji o planowanych przerwach.")

    st.divider()
    st.subheader("✉️ Test Powiadomień Służbowych")
    if st.button("Wyślij testowy alert na agroap.com.pl"):
        with st.spinner("Wysyłanie maila..."):
            res = send_email_alert("TEST: System Monitoringu", "Dashboard działa i monitoruje strony e-Doręczeń.")
            if res is True:
                st.success("Wysłano! Sprawdź skrzynkę (również folder Inne/Spam).")
            else:
                st.error(res)

with col_right:
    st.header("📅 Kalendarz Alertów")
    if any_alert:
        st.error("🔴 Dziś: Wykryto potencjalne utrudnienia!")
    else:
        st.success("🔵 Dziś: Wszystkie systemy operacyjne.")

st.caption("Dashboard v1.8 | Secure Email Alerts")

