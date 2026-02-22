import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v5.9
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- [ZAMROŻONE] 2. E-DORĘCZENIA ---
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

# --- 3. SYSTEM I SOFT - SMART PATH ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v59")
    st.divider()
    st.write("**Wersja:** v5.9")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    st.info("Sekcja zamrożona.")
    calendar(events=get_dynamic_gov_events(), options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth"},"initialView":"dayGridMonth","height":450,"locale":"pl","displayEventTime":False,"selectable":True}, key="cal_v59")

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Zarządzania Oprogramowaniem")
    
    st.subheader("1. Wygeneruj listę")
    st.code('Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "C:\\Test\\moje_programy.txt"', language='powershell')
    
    st.divider()
    
    st.subheader("2. Wgraj plik do analizy")
    
    # Podpowiedź ścieżki
    st.write("💡 **Wskazówka:** Po kliknięciu w przycisk poniżej, wklej tę ścieżkę w polu nazwy pliku, aby szybko tam przejść:")
    st.code("C:\\Test\\", language="text")
    
    up = st.file_uploader("Wybierz plik moje_programy.txt", type="txt")
    
    if up:
        raw = up.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')
            
        apps = []
        for line in text.splitlines():
            if line.strip() and "----" not in line and "DisplayName" not in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 1:
                    apps.append({"Oprogramowanie": parts[0], "Wersja": parts[1] if len(parts) > 1 else "---"})
        
        if apps:
            df = pd.DataFrame(apps).drop_duplicates().sort_values(by="Oprogramowanie")
            search = st.text_input("🔍 Filtruj listę (np. Norton, Epic, Java):")
            if search:
                df = df[df['Oprogramowanie'].str.contains(search, case=False, na=False)]
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Czekam na plik z folderu C:\\Test\\")
