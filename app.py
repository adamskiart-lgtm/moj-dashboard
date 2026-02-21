import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="E-Doręczenia Monitor", layout="wide")

# --- FUNKCJA 1: WYSYŁANIE MAILA (Używa Twoich Secrets) ---
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

# --- FUNKCJA 2: MONITOROWANIE STRON ---
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
        {
            "name": "Poczta Polska - Prace Serwisowe",
            "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/",
            "keywords": ["przerwa", "techniczna", "utrudnienia", "serwisowe"]
        },
        {
            "name": "GOV.PL - Niedostępność usługi",
            "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen",
            "keywords": ["niedostępność", "planowana", "awaria", "przerwa"]
        }
    ]

    any_alert = False
    for site in sites:
        status = check_service_status(site["url"], site["keywords"])
        with st.expander(f"🌐 {site['name']}", expanded=True):
            if status == "Błąd połączenia":
                st.error("Nie można pobrać danych ze strony.")
            elif isinstance(status, list):
                st.error(f"⚠️ Wykryto wzmianki o przerwach: {', '.join(status)}")
                any_alert = True
            else:
                st.success("✅ Brak informacji o planowanych przerwach.")

    st.divider()
    # PRZYCISK TESTOWY
    st.subheader("✉️ Test Powiadomień")
    if st.button("Wyślij testowy alert na maila służbowego"):
        with st.spinner("Wysyłanie..."):
            result = send_email_alert(
                "TEST: Dashboard Monitorujący", 
                f"Cześć Artur!\n\nTo jest testowa wiadomość z Twojego Dashboardu.\nData: {datetime.datetime.now()}"
            )
            if result is True:
                st.success("Mail wysłany! Sprawdź skrzynkę artur.adamski@agroap.com.pl (również SPAM).")
            else:
                st.error(f"Nie udało się wysłać: {result}")

with col_right:
    st.header("📅 Kalendarz Alertów")
    st.info(f"Dziś jest {datetime.date.today()}")
    
    st.markdown("### Legenda:")
    st.markdown("<p style='color:blue;'>🔵 Wszystko OK</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:red;'>🔴 Wykryto PRZERWĘ</p>", unsafe_allow_html=True)
    
    if any_alert:
        st.error("🔴 Dziś: Wykryto wzmianki o utrudnieniach!")
    else:
        st.success("🔵 Dziś: Brak komunikatów o przerwach.")

st.divider()
st.caption("Dashboard v1.8 | Email Alert System Integrated")
