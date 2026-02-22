import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v6.0 (Restored & Audited)
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. [SEKCJA PRZYWRÓCONA - ZAMROŻONA] E-DORĘCZENIA ---
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
                        events.append({
                            "id": event_id, "title": f"{time_range} | {podmiot}", "start": iso_date, "end": iso_date,
                            "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80", "display": "block", "allDay": True,
                            "extendedProps": {"pub_date": pub_date, "provider": podmiot}
                        })
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
        content = []
        for p in paragraphs:
            txt = p.get_text().strip()
            if "Informujemy" in txt:
                content.append(txt)
                parent = p.find_parent()
                if parent:
                    all_p_in_parent = parent.find_all('p')
                    start_idx = all_p_in_parent.index(p)
                    for next_p in all_p_in_parent[start_idx+1:]:
                        next_txt = next_p.get_text().strip()
                        content.append(next_txt)
                        if re.fullmatch(r'\d{2}\.\d{2}\.\d{4}', next_txt): break
                break
        return "\n\n".join(content) if content else "Brak aktywnych komunikatów."
    except: return "Błąd połączenia."

# --- 3. NAWIGACJA ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v60")
    st.divider()
    st.write("**Wersja:** v6.0")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(get_poczta_simple_alert())
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color:#007bff;font-weight:bold;">Strona Poczty Polskiej</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Przerwy widoczne w kalendarzu poniżej.")
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color:#007bff;font-weight:bold;">Strona GOV.PL</a>', unsafe_allow_html=True)
    st.divider()
    cal_data = calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="calendar_v60")
    if "eventClick" in cal_data:
        ev = cal_data["eventClick"]["event"]
        st.success(f"🔍 **Zgłosił:** {ev['extendedProps']['provider']} | **Publikacja:** {ev['extendedProps']['pub_date']}")

# --- 4. SYSTEM I SOFT - PEŁNA WERYFIKACJA ---
elif choice == "💻 System i Soft":
    st.header("💻 Audyt Oprogramowania Systemowego")
    
    # Baza najnowszych wersji do weryfikacji
    latest_versions = {
        "Adobe Photoshop": "27.3", "Norton 360": "22.24", "Epic Games": "15.0", 
        "Java": "8.0", "Edge": "145", "Total Commander": "10.0", "Fortnite": "28.0"
    }

    st.subheader("1. Generowanie danych")
    st.code('Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "C:\\Test\\moje_programy.txt"', language='powershell')
    
    st.divider()
    
    st.subheader("2. Weryfikacja plików")
    st.code("C:\\Test\\", language="text")
    up = st.file_uploader("Wgraj plik moje_programy.txt", type="txt", key="up_v60")
    
    if up:
        raw = up.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')
            
        audit_results = []
        for line in text.splitlines():
            if line.strip() and "----" not in line and "DisplayName" not in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 1:
                    name = parts[0]
                    version = parts[1] if len(parts) > 1 else "---"
                    
                    # Weryfikacja aktualności
                    status = "✅ Zainstalowano"
                    for key, v_target in latest_versions.items():
                        if key.lower() in name.lower():
                            try:
                                if float(version.split('.')[0]) < float(v_target.split('.')[0]):
                                    status = f"⚠️ Wymagany Update ({v_target})"
                                else:
                                    status = "✅ Aktualny"
                            except: status = "✅ Zweryfikowano"
                            break
                            
                    audit_results.append({"Oprogramowanie": name, "Twoja Wersja": version, "Status": status})
        
        if audit_results:
            df = pd.DataFrame(audit_results).drop_duplicates().sort_values(by="Oprogramowanie")
            st.success(f"Przeskanowano {len(df)} pozycji.")
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Wgraj plik z C:\\Test\\, aby przeprowadzić audyt wersji.")
