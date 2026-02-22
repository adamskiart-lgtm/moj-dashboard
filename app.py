import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v5.6
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
    except: return False

def run_daily_check(poczta_content):
    today = datetime.date.today().isoformat()
    if st.session_state.get('last_check') != today:
        if poczta_content != st.session_state.get('last_text', ""):
            if send_notification(f"🔔 Zmiana e-Doręczenia: {today}", poczta_content):
                st.session_state['last_check'] = today
                st.session_state['last_text'] = poczta_content

# --- [ZAMROŻONE] 3. FUNKCJE E-DORĘCZENIA ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia':'01','lutego':'02','marca':'03','kwietnia':'04','maja':'05','czerwca':'06','lipca':'07','sierpnia':'08','września':'09','października':'10','listopada':'11','grudnia':'12'}
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find('table').find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                raw = cols[0].get_text().strip().lower()
                podmiot = cols[1].get_text().strip()
                pub = cols[2].get_text().strip()
                try:
                    day = re.search(r'(\d{1,2})', raw).group(1).zfill(2)
                    month = months[next(m for m in months if m in raw)]
                    year = re.search(r'(202\d)', raw).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw)
                    t_range = f"{times[0]}-{times[1]}" if len(times)>=2 else "Planowana"
                    iso = f"{year}-{month}-{day}"
                    if not any(e.get('id') == f"{iso}_{podmiot}" for e in events):
                        events.append({"id":f"{iso}_{podmiot}","title":f"{t_range} | {podmiot}","start":iso,"end":iso,"backgroundColor":"#EE6C4D" if "PP" in podmiot else "#3D5A80","display":"block","allDay":True,"extendedProps":{"pub":pub,"prov":podmiot}})
                except: continue
        return events
    except: return []

def get_poczta_simple_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for p in soup.find_all('p'):
            txt = p.get_text().strip()
            if "Informujemy" in txt:
                content = [txt]
                for nxt in p.find_next_siblings('p'):
                    ntxt = nxt.get_text().strip()
                    content.append(ntxt)
                    if re.fullmatch(r'\d{2}\.\d{2}\.\d{4}', ntxt): break
                return "\n\n".join(content)
        return "Brak nowych komunikatów."
    except: return "Błąd połączenia."

# --- 4. INTERFEJS ---
current_poczta = get_poczta_simple_alert()
run_daily_check(current_poczta)

with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_final_v56")
    st.divider()
    st.write("**Wersja:** v5.6")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(current_poczta)
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color:#007bff;font-weight:bold;">Strona Poczty</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Przerwy w kalendarzu poniżej.")
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color:#007bff;font-weight:bold;">Strona GOV</a>', unsafe_allow_html=True)
    st.divider()
    cal = calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="cal_v56")
    if "eventClick" in cal:
        e = cal["eventClick"]["event"]
        st.success(f"🔍 **Zgłosił:** {e['extendedProps']['prov']} | **Publikacja:** {e['extendedProps']['pub']}")

elif choice == "💻 System i Soft":
    st.header("💻 Skaner Systemowy")
    st.subheader("Krok 1: Wygeneruj plik")
    st.write("Wklej w PowerShell (Admin):")
    st.code('Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "C:\\Test\\moje_programy.txt"', language='powershell')
    
    st.subheader("Krok 2: Wgraj do analizy")
    up = st.file_uploader("Wgraj plik moje_programy.txt z folderu C:\\Test", type="txt")
    if up:
        raw = up.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')
        targets = {"Adobe Photoshop":"27.3","Java":"8.0","ESET":"11.0","Cyberpunk 2077":"2.1","Total Commander":"10.0","Edge":"145"}
        res = []
        for app, target in targets.items():
            m = re.search(f"{app}.*?(\d+[\d\.]*)", text, re.I)
            v = m.group(1) if m else "Brak"
            status = "✅ OK" if v != "Brak" and v >= target else ("❌ Brak" if v == "Brak" else f"⚠️ Update do {target}")
            res.append({"Program":app, "Wersja":v, "Status":status})
        st.table(res)
