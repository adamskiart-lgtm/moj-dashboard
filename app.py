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

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. FUNKCJE (MAIL, SCRAPING) ---

def send_full_alert(subject, context_text):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroapp.com.pl"
        
        date_pattern = r'(\d{1,2}\.\d{1,2}(?:\.\d{4})?)'
        time_pattern = r'(\d{1,2}:\d{2})'
        dates = re.findall(date_pattern, context_text)
        times = re.findall(time_pattern, context_text)
        
        start_dt = datetime.datetime.now()
        if dates and times:
            try:
                d, m = map(int, dates[0].split('.')[:2])
                h, mi = map(int, times[0].split(':'))
                start_dt = datetime.datetime(start_dt.year, m, d, h, mi)
            except: pass

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Monitor Systemowy <{sender_email}>"
        msg['To'] = receiver_email
        msg.attach(MIMEText(f"Wykryto przerwę!\n\nKOMUNIKAT:\n{context_text}", 'plain'))

        ics_content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}\nSUMMARY:Przerwa e-Doręczenia\nEND:VEVENT\nEND:VCALENDAR"
        part = MIMEBase('text', 'calendar', method='REQUEST', name='przerwa.ics')
        part.set_payload(ics_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="przerwa.ics"')
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e: return str(e)

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

# --- 3. PASEK BOCZNY (SIDEBAR MENU) ---
with st.sidebar:
    st.title("📂 Panel Sterowania")
    choice = st.radio(
        "N
