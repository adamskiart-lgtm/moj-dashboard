import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v5.2
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- [SEKCJA ZAMROŻONA] 2. E-DORĘCZENIA ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04', 'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08', 'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'}
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
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Brak godz."
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
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            txt = p.get_text().strip()
            if "Informujemy" in txt:
                content = [txt]
                parent = p.find_parent()
                if parent:
                    all_p = parent.find_all('p')
                    start_idx = all_p.index(p)
                    for next_p in all_p[start_idx+1:]:
                        next_txt = next_p.get_text().strip()
                        content.append(next_txt)
                        if re.fullmatch(r'\d{2}\.\d{2}\.\d{4}', next_txt): break
                return "\n\n".join(content)
        return "Brak aktywnych komunikatów."
    except: return "Błąd połączenia."

# --- 3. NAWIGACJA ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v52")
    st.divider()
    st.write(f"**Wersja kodu:** v5.2")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(get_poczta_simple_alert())
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color: #007bff; font-weight: bold;">Strona Poczty Polskiej</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Harmonogram pobierany automatycznie poniżej.")
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color: #007bff; font-weight: bold;">Strona GOV.PL</a>', unsafe_allow_html=True)
    st.divider()
    calendar(events=get_dynamic_gov_events(), options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False, "selectable": True}, key="calendar_v52")

# --- 4. SYSTEM I SOFT ---
elif choice == "💻 System i Soft":
    st.header("💻 Centrum Diagnostyki Systemowej")
    
    st.subheader("Step 1: Pobierz dane z systemu")
    st.write("Skopiuj poniższą komendę i wklej ją do niebieskiego okna **PowerShell** (jako Administrator):")
    
    # Blok kodu do skopiowania
    cmd = 'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "$env:USERPROFILE\\Desktop\\moje_programy.txt"'
    st.code(cmd, language='powershell')
    
    st.subheader("Step 2: Analiza")
    up_file = st.file_uploader("Wgraj utworzony plik moje_programy.txt z Pulpitu", type="txt", key="uploader_v52")

    if up_file:
        raw = up_file.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')
        
        target_apps = {
            "Adobe Photoshop": "27.3", "Java": "8.0", "ESET": "11.0", 
            "Cyberpunk 2077": "2.1", "Total Commander": "10.0", "Edge": "145"
        }
        
        results = []
        for app, target_v in target_apps.items():
            match = re.search(f"{app}.*?(\d+\\.\\d+)", text, re.IGNORECASE)
            if match:
                current_v = match.group(1)
                status = "✅ OK" if current_v >= target_v else f"⚠️ Update do {target_v}"
                results.append({"Program": app, "Wersja": current_v, "Status": status})
            else:
                results.append({"Program": app, "Wersja": "Brak", "Status": "❌ Nie wykryto"})
        
        st.table(results)
    else:
        st.info("💡 Po uruchomieniu komendy w PowerShellu, plik pojawi się na Twoim Pulpicie. Wgraj go tutaj.")
