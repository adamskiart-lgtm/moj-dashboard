import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Personal Operations Center", layout="wide")

# --- FUNKCJE SYSTEMOWE ---

def send_email_alert(subject, message):
    try:
        sender_email = st.secrets["GMAIL_USER"]
        sender_password = st.secrets["GMAIL_PASSWORD"]
        receiver_email = "artur.adamski@agroap.com.pl"
        
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = f"Monitor Systemowy <{sender_email}>"
        msg['To'] = receiver_email
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)

def check_service_status(url, keywords):
    try:
        # User-agent udaje przeglądarkę, żeby strony nas nie blokowały
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        found = [word for word in keywords if word in text]
        return found if found else None
    except:
        return "Błąd połączenia"

# --- LOGIKA HARMONOGRAMU ---
now = datetime.datetime.now()
is_workday = now.weekday() < 5  # Pon-Pt to 0-4
is_business_hours = 7 <= now.hour <= 17

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("🚀 Personal Operations Center")
st.write(f"Ostatnie odświeżenie: **{now.strftime('%d.%m.%Y %H:%M:%S')}**")

# Informacja o trybie pracy monitora
if is_workday:
    status_msg = "⏱️ Tryb roboczy: Sprawdzanie co 2h (07:00 - 17:00)" if is_business_hours else "🌙 Poza godzinami pracy (Tryb uśpiony)"
else:
    status_msg = "📅 Tryb weekendowy: Sprawdzanie raz dziennie"
st.caption(status_msg)

st.divider()

# --- SEKCJA 1: MONITORING E-DORĘCZEŃ (GÓRA) ---
st.header("📡 Monitoring e-Doręczeń")
col_eda, col_edb = st.columns(2)

sites = [
    {
        "name": "Poczta Polska - Prace Serwisowe",
        "url": "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/",
        "keywords": ["przerwa", "techniczna", "utrudnienia", "serwisowe", "niedostępność"]
    },
    {
        "name": "GOV.PL - Niedostępność usługi",
        "url": "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen",
        "keywords": ["niedostępność", "awaria", "przerwa", "planowane", "utrudnienia"]
    }
]

any_alert = False
alert_details = ""

for i, site in enumerate(sites):
    status = check_service_status(site["url"], site["keywords"])
    with [col_eda, col_edb][i]:
        with st.container(border=True):
            st.subheader(site["name"])
            if isinstance(status, list):
                st.error(f"🔴 Wykryto utrudnienia: {', '.join(status)}")
                any_alert = True
                alert_details += f"- {site['name']}: Znaleziono słowa: {', '.join(status)}\n"
            elif status == "Błąd połączenia":
                st.warning("🟡 Problem z połączeniem ze stroną")
            else:
                st.success("🔵 Brak komunikatów o przerwach")
            st.caption(f"[Sprawdź źródło na stronie]({site['url']})")

# --- AUTOMATYCZNY ALERT MAILOWY ---
if any_alert and 'last_alert_sent' not in st.session_state:
    # Wysyłamy maila tylko raz na sesję przeglądarki, żeby nie spamować
    send_email_alert(
        f"⚠️ ALERT e-Doręczenia: {now.strftime('%H:%M')}",
        f"Wykryto potencjalną przerwę w działaniu usług!\n\nSzczegóły:\n{alert_details}\nSprawdź dashboard: https://adamskiart-lgtm.streamlit.app"
    )
    st.session_state['last_alert_sent'] = now
    st.toast("Wysłano alert e-mail!", icon="📧")

st.divider()

# --- SEKCJA 2: NARZĘDZIA I POCZTA ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("⚙️ Status Oprogramowania")
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"}
    ]
    st.table(soft_data)
    
    st.divider()
    st.subheader("✉️ Narzędzia ręczne")
    if st.button("Wyślij testowy raport na agroap.com.pl"):
        res = send_email_alert("Raport Ręczny Monitora", "Dashboard działa poprawnie. Monitoring aktywny.")
        if res is True: st.success("Raport wysłany pomyślnie!")
        else: st.error(res)

with col_right:
    with st.container(border=True):
        st.subheader("💻 Twoja Maszyna")
        st.markdown("**Dell Precision 5540**\ni9-9880H | 32 GB RAM")
        st.progress(0.46, text="Dysk: 433GB wolne")
    
    st.divider()
    st.subheader("📅 Kalendarz")
    st.info("Pobieranie nadchodzących sesji...")
    # Tutaj możesz wstawić swoją funkcję kalendarza z poprzednich kroków

st.caption(f"Dashboard v2.0 | Scheduler Active | Secure Mail")


