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
# Wersja kodu: v7.8 [2026-02-22]
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# CSS: Czytelne metryki i mniejsza czcionka tabeli
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700; color: #1E3A8A; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; }
    .stDataFrame { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIKA POWIADOMIEŃ E-MAIL ---
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

# --- 3. [PRZYWRÓCONA] SEKCJA E-DORĘCZENIA ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia':'01','lutego':'02','marca':'03','kwietnia':'04','maja':'05','czerwca':'06','lipca':'07','sierpnia':'08','września':'09','października':'10','listopada':'11','grudnia':'12'}
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table: return []
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                raw_dt = cols[0].get_text().strip().lower()
                podmiot = cols[1].get_text().strip()
                pub_date = cols[2].get_text().strip()
                try:
                    day = re.search(r'(\d{1,2})', raw_dt).group(1).zfill(2)
                    month = months[next(m for m in months if m in raw_dt)]
                    year = re.search(r'(202\d)', raw_dt).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw_dt)
                    t_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso = f"{year}-{month}-{day}"
                    if not any(e.get('id') == f"{iso}_{podmiot}" for e in events):
                        events.append({"id": f"{iso}_{podmiot}", "title": f"{t_range} | {podmiot}", "start": iso, "end": iso, "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80", "display": "block", "allDay": True, "extendedProps": {"pub_date": pub_date, "provider": podmiot}})
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

# --- 4. NAWIGACJA ---
current_poczta = get_poczta_simple_alert()
run_daily_check(current_poczta)

with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v78")
    st.divider()
    st.write("**Wersja:** v7.8")

# --- 5. WIDOK: E-DORĘCZENIA (PRZYWRÓCONY) ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(current_poczta)
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color:#007bff;font-weight:bold;">Strona Poczty Polskiej</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Przerwy widoczne w kalendarzu poniżej.")
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color:#007bff;font-weight:bold;">Strona GOV.PL</a>', unsafe_allow_html=True)
    st.divider()
    cal_data = calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="cal_v78")
    if "eventClick" in cal_data:
        ev = cal_data["eventClick"]["event"]
        st.success(f"🔍 **Zgłosił:** {ev['extendedProps']['provider']} | **Publikacja:** {ev['extendedProps']['pub_date']}")

# --- 6. WIDOK: SYSTEM I SOFT (FINALNA NAPRAWA SPRZĘTU) ---
elif choice == "💻 System i Soft":
    st.header("💻 Audyt Sprzętowo-Programowy")
    
    app_meta = {
        "Adobe Photoshop": {"target": "27.3", "url": "https://www.adobe.com/pl/creativecloud/desktop.html"},
        "Norton": {"target": "22.24", "url": "https://my.norton.com/"},
        "Epic Games": {"target": "15.0", "url": "https://www.epicgames.com/site/pl/home"},
        "Fortnite": {"target": "28.0", "url": "https://www.epicgames.com/fortnite/pl/download"},
        "Java": {"target": "8.0", "url": "https://www.java.com/pl/download/"},
        "NVIDIA": {"target": "550", "url": "https://www.nvidia.pl/Download/index.aspx?lang=pl"}
    }

    st.subheader("1. Wykonaj Raport (PowerShell Admin)")
    # NOWA KOMENDA - Zmiana zapisu na ASCII (najbezpieczniejszy format tekstowy)
    ps_cmd = (
        "powershell -Command \"Write-Output 'MODEL:' (Get-CimInstance Win32_ComputerSystem).Model | Out-File C:\\Test\\raport_systemowy.txt -Encoding ascii; "
        "Write-Output 'CPU:' (Get-CimInstance Win32_Processor).Name | Out-File C:\\Test\\raport_systemowy.txt -Append -Encoding ascii; "
        "Write-Output 'RAM:' ((Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1GB) 'GB' | Out-File C:\\Test\\raport_systemowy.txt -Append -Encoding ascii; "
        "Write-Output 'GPU:' (Get-CimInstance Win32_VideoController).Name | Out-File C:\\Test\\raport_systemowy.txt -Append -Encoding ascii; "
        "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
        "Select-Object DisplayName, DisplayVersion | Out-File C:\\Test\\raport_systemowy.txt -Append -Encoding ascii; exit\""
    )
    st.code(ps_cmd, language='powershell')

    st.divider()
    up = st.file_uploader("2. Wgraj raport z C:\\Test\\raport_systemowy.txt", type="txt", key="up_v78")

    if up:
        # Odczytujemy plik próbując różnych kodowań
        raw_bytes = up.read()
        encodings = ['ascii', 'utf-8', 'utf-16']
        text = ""
        for enc in encodings:
            try:
                text = raw_bytes.decode(enc)
                if "MODEL:" in text: break
            except: continue
            
        lines = text.splitlines()
        hw = {'Model': 'N/A', 'CPU': 'N/A', 'RAM': 'N/A', 'GPU': 'N/A'}
        
        for line in lines:
            l_up = line.upper()
            if "MODEL:" in l_up: hw['Model'] = line.split(':', 1)[1].strip()
            elif "CPU:" in l_up: hw['CPU'] = line.split(':', 1)[1].strip().split('@')[0]
            elif "RAM:" in l_up: hw['RAM'] = line.split(':', 1)[1].strip()
            elif "GPU:" in l_up: hw['GPU'] = line.split(':', 1)[1].strip()

        st.success("✅ Dane sprzętowe:")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Maszyna", hw['Model'])
        c2.metric("Procesor", hw['CPU'])
        c3.metric("RAM", hw['RAM'])
        c4.metric("Grafika", hw['GPU'])
        
        st.divider()
        
        results, updates = [], []
        for line in lines:
            if any(x in line.upper() for x in ["MODEL:", "CPU:", "RAM:", "GPU:", "DISPLAYNAME"]): continue
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 1 and len(parts[0]) > 2:
                name, ver = parts[0], (parts[1] if len(parts) > 1 else "---")
                status = "✅ OK"
                for key, meta in app_meta.items():
                    if key.lower() in name.lower():
                        try:
                            curr_v = int(re.search(r'\d+', ver).group())
                            target_v = int(re.search(r'\d+', meta["target"]).group())
                            if curr_v < target_v:
                                status = f"⚠️ Update do {meta['target']}"
                                updates.append({"n": name, "u": meta["url"]})
                        except: pass
                results.append({"Program": name, "Wersja": ver, "Status": status})

        if results:
            df = pd.DataFrame(results).drop_duplicates().sort_values(by="Program")
            st.dataframe(df, use_container_width=True, hide_index=True)
            if updates:
                st.subheader("🚀 Instrukcja Aktualizacji")
                for itm in updates: st.warning(f"**{itm['n']}** ➔ [Pobierz stąd]({itm['u']})")
