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
# Wersja kodu: v6.3 [2026-02-22]
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. LOGIKA MONITOROWANIA I E-MAIL (ZAMROŻONA) ---
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

# --- 3. [SEKCJA ZAMROŻONA] FUNKCJE E-DORĘCZENIA ---
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
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v63")
    st.divider()
    st.write("**Wersja:** v6.3")

# --- 5. WIDOK: E-DORĘCZENIA (ZAMROŻONY) ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(current_poczta)
        st.markdown('[➔ Strona Poczty Polskiej](https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/)')
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Przerwy widoczne w kalendarzu poniżej.")
        st.markdown('[➔ Strona GOV.PL](https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen)')
    st.divider()
    cal_data = calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="cal_v63")
    if "eventClick" in cal_data:
        ev = cal_data["eventClick"]["event"]
        st.success(f"🔍 **Zgłosił:** {ev['extendedProps']['provider']} | **Publikacja:** {ev['extendedProps']['pub_date']}")

# --- 6. WIDOK: SYSTEM I SOFT ---
elif choice == "💻 System i Soft":
    st.header("💻 Audyt i Hub Aktualizacji")
    st.info("💻 **Dell Precision 5540** | i9 | Quadro T2000 | [Pobierz Sterowniki Dell](https://www.dell.com/support/home/pl-pl/product-support/product/precision-15-5540-laptop/drivers)")
    
    # Baza linków i wersji
    app_meta = {
        "Adobe": {"target": "27.0", "url": "https://www.adobe.com/pl/creativecloud/desktop.html"},
        "Norton": {"target": "22.0", "url": "https://my.norton.com/"},
        "Epic": {"target": "15.0", "url": "https://www.epicgames.com/store/pl/download"},
        "Fortnite": {"target": "28.0", "url": "https://www.epicgames.com/fortnite/pl/download"},
        "Java": {"target": "8.0", "url": "https://www.java.com/pl/download/"},
        "Edge": {"target": "140", "url": "https://www.microsoft.com/pl-pl/edge"},
        "Total Commander": {"target": "11.0", "url": "https://www.ghisler.com/download.htm"},
        "NVIDIA": {"target": "550", "url": "https://www.nvidia.pl/Download/index.aspx?lang=pl"}
    }

    st.subheader("1. Generowanie raportu (PowerShell Admin)")
    st.code('Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "C:\\Test\\moje_programy.txt"', language='powershell')
    
    st.divider()
    up = st.file_uploader("Wgraj plik moje_programy.txt z C:\\Test\\", type="txt", key="up_v63")
    
    if up:
        raw = up.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')
            
        results = []
        lines = text.splitlines()
        for line in lines:
            if line.strip() and "----" not in line and "DisplayName" not in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 1:
                    name, ver = parts[0], (parts[1] if len(parts) > 1 else "---")
                    status, download_url = "✅ OK", None
                    
                    for key, data in app_meta.items():
                        if key.lower() in name.lower():
                            download_url = data["url"]
                            try:
                                if float(ver.split('.')[0]) < float(data["target"].split('.')[0]):
                                    status = f"⚠️ Wymagany Update"
                            except: status = "✅ Zweryfikowano"
                            break
                    results.append({"Program": name, "Wersja": ver, "Status": status, "Link": download_url})
        
        if results:
            df = pd.DataFrame(results).drop_duplicates().sort_values(by="Program")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("📋 Szybka Ścieżka Aktualizacji")
            updates_needed = [r for r in results if "⚠️" in r['Status']]
            
            if updates_needed:
                for item in updates_needed:
                    st.markdown(f"**{item['Program']}** ➔ [Kliknij, aby pobrać/zaktualizować]({item['Link']})")
                st.warning("💡 Pamiętaj o restartowaniu systemu po instalacji sterowników NVIDIA Quadro.")
            else:
                st.success("System jest w pełni zoptymalizowany. Nie wykryto przestarzałych aplikacji.")
