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

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="E-Doręczenia Monitor PRO", layout="wide")

# --- FUNKCJA WYCIĄGANIA DATY Z TEKSTU ---
def extract_dates(text):
    # Szukamy daty w formacie DD.MM.YYYY lub DD.MM
    date_pattern = r'(\d{1,2}\.\d{1,2}(?:\.\d{4})?)'
    # Szukamy godziny w formacie HH:MM
    time_pattern = r'(\d{1,2}:\d{2})'
    
    found_dates = re.findall(date_pattern, text)
    found_times = re.findall(time_pattern, text)
    
    return found_dates, found_times

# --- FUNKCJA WYSYŁANIA MAILA Z INTELIGENTNYM ZAPROSZENIEM ---
def send_email_with_invite(subject, message, context_text):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroapp.com.pl"
        
        # Analiza daty z komunikatu
        dates, times = extract_dates(context_text)
        
        # Próba ustawienia czasu startu na podstawie tekstu
        start_dt = datetime.datetime.now() + datetime.timedelta(hours=1)
        if dates and times:
            try:
                # Próba złożenia daty z pierwszej znalezionej pary
                day, month = map(int, dates[0].split('.')[:2])
                hour, minute = map(int, times[0].split(':'))
                year = start_dt.year
                start_dt = datetime.datetime(year, month, day, hour, minute)
            except:
                pass

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"Monitor e-Doręczeń <{sender_email}>"
        msg['To'] = receiver_email
        
        body = f"{message}\n\nFRAGMENT KOMUNIKATU ZE STRONY:\n{context_text}"
        msg.attach(MIMEText(body, 'plain'))

        # Plik .ics (Zaproszenie)
        end_dt = start_dt + datetime.timedelta(hours=4) # Domyślnie 4h przerwy
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:PRZERWA: E-Doręczenia
DESCRIPTION:{context_text[:200]}
END:VEVENT
END:VCALENDAR"""

        part = MIMEBase('text', 'calendar', method='REQUEST', name='termin_przerwy.ics')
        part.set_payload(ics_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="termin_przerwy.ics"')
        msg.attach(part)

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
        
        # Usuwamy eArchiwum z analizy
        for tag in soup.find_all(string=re.compile("earchiwum", re.I)):
            if tag.parent: tag.parent.extract()
            
        text = soup.get_text()
        text_lower = text.lower()
        found = [word for word in keywords if word in text_lower]
        
        context = ""
        if found:
            # Szukamy gdzie wystąpiło słowo kluczowe i bierzemy otoczenie (150 znaków)
            idx = text_lower.find(found[0])
            context = text[max(0, idx-50):min(len(text), idx+200)].strip()
            
        return (found, context) if found else (None, "")
    except:
        return ("Błąd połączenia", "")

# --- GŁÓWNY INTERFEJS ---
st.title("📡 Smart Monitor e-Doręczeń")
now = datetime.datetime.now()

col_eda, col_edb = st.columns(2)
sites = [
    {"name": "Poczta Polska", "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", "keywords": ["przerwa", "techniczna", "utrudnienia"]},
    {"name": "GOV.PL", "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", "keywords": ["niedostępność", "awaria", "przerwa"]}
]

any_alert = False

for i, site in enumerate(sites):
    status, context = check_service_status(site["url"], site["keywords"])
    with [col_eda, col_edb][i]:
        with st.container(border=True):
            st.subheader(site["name"])
            if status:
                st.error(f"🔴 Wykryto komunikat!")
                st.write(f"**Treść:** {context}")
                
                # Przycisk wysyłki ręcznej dla konkretnego komunikatu
                if st.button(f"Wyślij to zaproszenie na agroapp", key=site['name']):
                    res = send_email_with_invite(f"⚠️ Terminy przerwy: {site['name']}", "Szczegóły przerwy odczytane ze strony.", context)
                    if res is True: st.success("Wysłano!")
                    else: st.error(res)
                any_alert = True
            else:
                st.success("🔵 Brak utrudnień")

# --- AUTO-ALERT (Tylko raz na sesję) ---
if any_alert and 'sent' not in st.session_state:
    # Tutaj logika mogłaby automatycznie wysłać maila, 
    # ale przycisk powyżej daje Ci kontrolę nad tym, co wysyłasz.
    st.session_state['sent'] = True

st.divider()
st.caption(f"v2.3 | Adres: artur.adamski@agroapp.com.pl | Auto-Date Detection | No eArchiwum")
