import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v6.2 [2026-02-22]
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. LOGIKA MONITOROWANIA I E-MAIL ---
def send_notification(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = st.secrets["email_user"]
        msg['To'] = "artur.adamski@agroapp.com.pl"
        with smtplib.SMTP_SSL(st.secrets["email_host"], st.secrets["email_port"]) as server:
            server.login(st.secrets["email_user"], st.secrets["email_password"])
            server.send_message(msg)
        return True
    except:
        return False

def run_daily_check(poczta_content):
    today = datetime.date.today().isoformat()
    if st.session_state.get('last_check') != today:
        if poczta_content != st.session_state.get('last_text', ""):
            if send_notification(f"🔔 Zmiana e-Doręczenia: {today}", poczta_content):
                st.session_state['last_check'] = today
                st.session_state['last_text'] = poczta_content

# --- 3. [SEKCJA ZAMROŻONA] FUNKCJE E-DORĘCZENIA ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia':'01','lutego':'02','marca':'03','kwietnia':'04','maja':'05','czerwca':'06','lipca':'07','sierpnia':'08','września':'09','października':'10','listopada':'11','grudnia':'12'}
    try:
