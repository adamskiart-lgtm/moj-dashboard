import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="E-Doręczenia Monitor PRO", layout="wide")

# --- FUNKCJA WYSYŁANIA MAILA Z ZAPROSZENIEM ---
def send_email_with_invite(subject, message, start_dt):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroapp.com.pl"
        
        # Tworzenie kontenera wiadomości
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Monitor Systemowy <{sender_email}>"
        msg['To'] = receiver_email
        msg.attach(MIMEText(message, 'plain'))

        # Tworzenie treści zaproszenia .ics
        end_dt = start_dt + datetime.timedelta(hours=2)
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Monitor Dashboard//PL
BEGIN:VEVENT
UID:{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}@monitor.com
DTSTAMP:{datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Niedostępność E-Doręczeń (ALERT)
DESCRIPTION:{message.replace('\\n', ' ')}
LOCATION:Strony rządowe / Poczta Polska
END:VEVENT
END:VCALENDAR"""

        # Dodawanie załącznika .ics
        part = MIMEBase('text', 'calendar', method='REQUEST', name='zaproszenie.ics')
        part.set_payload(ics_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="zaproszenie.ics"')
        msg.attach(part)

        # Wysyłka
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)

# --- FUNKCJA MONITOROWANIA ---
def check_service_status(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Filtr eArchiwum
        for archive_div in soup.find_all(string=lambda text: "earchiwum" in text.lower()):
            if archive_div.parent: archive_div.parent.extract()
            
        text = soup.get_text().lower()
        found = [word for word in keywords if word in text]
        
        context = ""
        if found:
            start_idx = text.find(found[0])
            context = "..." + text[max(0, start_idx-60):min(len(text), start_idx+120)] + "..."
            
        return (found, context) if found else (None, "")
    except:
        return ("Błąd połączenia", "")

# --- LOGIKA GŁÓWNA ---
now = datetime.datetime.now()
st.title("📡 System Monitorowania E-Doręczeń")
st.write(f"Ostatnia weryfikacja: **{now.strftime('%H:%M:%S')}**")

st.divider()

# --- MONITORING (GÓRA) ---
col_eda, col_edb = st.columns(2)
sites = [
    {"name": "Poczta Polska", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["przerwa", "techniczna", "utrudnienia"]},
    {"name": "GOV.PL", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "awaria", "przerwa"]}
]

any_alert = False
alert_summary = ""

for i, site in enumerate(sites):
    status, context = check_service_status(site["url"], site["keywords"])
    with [col_eda, col_edb][i]:
        with st.container(border=True):
            st.subheader(site["name"])
            if status == "Błąd połączenia":
                st.warning("🟡 Problem z połączeniem")
            elif status:
                st.error(f"🔴 WYKRYTO ZMIANĘ: {', '.join(status)}")
                st.info(f"**Kontekst:** {context}")
                any_alert = True
                alert_summary += f"{site['name']}: {', '.join(status)}. "
            else:
                st.success("🔵 System dostępny")

# --- AKCJE AUTOMATYCZNE ---
if any_alert and 'alert_sent' not in st.session_state:
    # Wysyłka maila z zaproszeniem ICS
    res = send_email_with_invite(
        f"⚠️ ALERT: Przerwa e-Doręczenia ({now.strftime('%d.%m')})",
        f"Wykryto utrudnienia. Szczegóły: {alert_summary}",
        now
    )
    if res is True:
        st.toast("Wysłano alert z zaproszeniem!", icon="📧")
    st.session_state['alert_sent'] = True

st.divider()

# --- PANEL DOLNY ---
c1, c2 = st.columns([2, 1])
with c1:
    st.header("⚙️ Narzędzia")
    if st.button("Wyślij TESTOWE ZAPROSZENIE na agroapp.com.pl"):
        send_email_with_invite("TEST: Zaproszenie z Monitora", "Test działania załącznika ICS.", now)
        st.success("Testowe zaproszenie wysłane!")

with c2:
    with st.container(border=True):
        st.subheader("💻 Stacja")
        st.write("Dell Precision 5540 | i9")
        st.progress(0.46)

st.caption(f"v2.2 | Mail: artur.adamski@agroapp.com.pl | eArchiwum Ignored | ICS Support")
