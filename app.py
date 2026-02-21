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
        "Nawigacja:",
        ["📡 e-Doręczenia", "💻 System i Oprogramowanie"]
    )
    st.divider()
    st.info(f"Użytkownik: Artur\nGodzina: {datetime.datetime.now().strftime('%H:%M')}")
    if st.button("Wyślij test ICS na agroapp"):
        send_full_alert("Ręczny test systemu", "Wszystko działa poprawnie.")
        st.success("Wysłano!")

# --- 4. LOGIKA WYŚWIETLANIA ---

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    st.write("Weryfikacja dostępności usług Poczty Polskiej i GOV.PL.")
    
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
                    st.error(f"🔴 WYKRYTO: {', '.join(found)}")
                    st.write(f"**Treść:** {context}")
                    if st.button(f"Wyślij zaproszenie ({site['name']})", key=site['name']):
                        send_full_alert(f"⚠️ Alert: {site['name']}", context)
                        st.success("Wysłano!")
                else:
                    st.success("🔵 System dostępny")
                st.caption(f"[Źródło]({site['url']})")

elif choice == "💻 System i Oprogramowanie":
    st.header("💻 Centrum Systemowe")
    
    # Góra: Informacje o sprzęcie
    col_cpu, col_disk = st.columns(2)
    with col_cpu:
        with st.container(border=True):
            st.subheader("Specyfikacja Dell Precision 5540")
            st.write("🚀 **Procesor:** Intel Core i9-9880H")
            st.write("🧠 **Pamięć:** 32 GB RAM")
            st.write("🎨 **Grafika:** Quadro T2000")
    
    with col_disk:
        with st.container(border=True):
            st.subheader("Zasoby lokalne")
            st.progress(0.46, text="Dysk C: 433GB wolne")
            st.write("🔋 **Bateria:** 82% (Kondycja dobra)")

    st.divider()
    
    # Dół: Tabela oprogramowania
    st.subheader("⚙️ Status Oprogramowania")
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"}
    ]
    st.table(soft_data)

    st.divider()
    st.subheader("📅 Nadchodzące sesje (Kalendarz)")
    st.info("📌 25.02 - Sesja produktowa / Retusz")

# --- STOPKA ---
st.sidebar.caption(f"v2.6 | artur.adamski@agroapp.com.pl")
