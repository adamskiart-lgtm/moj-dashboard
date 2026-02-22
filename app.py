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
# Wersja kodu: v7.1 [2026-02-22]
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- CSS: ZMNIEJSZENIE CZCIONKI METRYK ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. [ZAMROŻONE] LOGIKA MONITOROWANIA I E-MAIL ---
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

# --- 3. [ZAMROŻONE] FUNKCJE E-DORĘCZENIA ---
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
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso_date = f"{year}-{month}-{day}"
                    event_id = f"{iso_date}_{podmiot}"
                    if not any(e.get('id') == event_id for e in events):
                        events.append({"id": event_id, "title": f"{time_range} | {podmiot}", "start": iso_date, "end": iso_date, "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80", "display": "block", "allDay": True, "extendedProps": {"pub_date": pub_date, "provider": podmiot}})
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
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v71")
    st.divider()
    st.write("**Wersja:** v7.1")

# --- 5. WIDOK: E-DORĘCZENIA (ZAMROŻONY) ---
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
    calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="cal_v71")

# --- 6. WIDOK: SYSTEM I SOFT (ONE-CLICK & AUTO-CLOSE) ---
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

    st.subheader("1. Wykonaj Raport (Kopiuj i wklej do PowerShell)")
    # KOMENDA: Generuje raport i zamyka okno (exit)
    ps_command = (
        "powershell -Command \"$hw = @{ 'Model' = (Get-CimInstance Win32_ComputerSystem).Model; "
        "'CPU' = (Get-CimInstance Win32_Processor).Name; "
        "'RAM' = \\\"$([Math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB)) GB\\\"; "
        "'GPU' = (Get-CimInstance Win32_VideoController).Name }; "
        "$hw.GetEnumerator() | ForEach-Object { \\\"$($_.Key): $($_.Value)\\\" } | Out-File 'C:\\Test\\raport_systemowy.txt' -Encoding utf8; "
        "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
        "Select-Object DisplayName, DisplayVersion | Format-List | Out-File 'C:\\Test\\raport_systemowy.txt' -Append -Encoding utf8; "
        "exit\""
    )
    st.code(ps_command, language='powershell')
    st.caption("💡 Po uruchomieniu raportu okno konsoli zamknie się automatycznie.")

    st.divider()
    up = st.file_uploader("Wgraj raport z C:\\Test\\raport_systemowy.txt", type="txt", key="up_v71")

    if up:
        raw_text = up.read().decode('utf-8', errors='ignore')
        st.success("✅ Raport wczytany!")
        
        # --- ODCZYT SPRZĘTU ---
        hw = {'Model': 'N/A', 'CPU': 'N/A', 'RAM': 'N/A', 'GPU': 'N/A'}
        lines = raw_text.splitlines()
        for line in lines:
            if ":" in line:
                key_part = line.split(":")[0].strip()
                val_part = line.split(":")[1].strip()
                if key_part in hw: hw[key_part] = val_part

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Model Maszyny", hw['Model'])
        c2.metric("Procesor", hw['CPU'].split('@')[0].strip())
        c3.metric("Pamięć RAM", hw['RAM'])
        c4.metric("Karta Graficzna", hw['GPU'])
        
        st.divider()
        
        # --- ANALIZA PROGRAMÓW ---
        results = []
        updates = []
        current_name = ""
        for line in lines:
            if "DisplayName :" in line: current_name = line.split(":")[-1].strip()
            if "DisplayVersion :" in line and current_name:
                ver = line.split(":")[-1].strip()
                status = "✅ OK"
                for key, meta in app_meta.items():
                    if key.lower() in current_name.lower():
                        try:
                            if float(ver.split('.')[0]) < float(meta["target"].split('.')[0]):
                                status = f"⚠️ Update do {meta['target']}"
                                updates.append({"name": current_name, "url": meta["url"]})
                        except: pass
                results.append({"Program": current_name, "Wersja": ver, "Status": status})
                current_name = ""
        
        if results:
            df = pd.DataFrame(results).drop_duplicates().sort_values(by="Program")
            st.subheader("📋 Wykryte Oprogramowanie")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if updates:
                st.divider()
                st.subheader("🚀 Instrukcja Aktualizacji")
                for item in updates:
                    st.warning(f"**{item['name']}** ➔ [Pobierz stąd]({item['url']})")
