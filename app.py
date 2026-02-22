import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v5.0 (Scanner & Inventory)
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- [SEKCJA ZAMROŻONA] 2. E-DORĘCZENIA (KALENDARZ I ALERTY) ---
# (Kod funkcji get_dynamic_gov_events i get_poczta_simple_alert pozostaje bez zmian)
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

# --- 3. INTERFEJS I NAWIGACJA ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v50")
    st.divider()
    st.write(f"**Wersja kodu:** v5.0")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(get_poczta_simple_alert())
        st.markdown('<a href="..." style="color: #007bff; font-weight: bold;">Strona Poczty Polskiej</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Przerwy widoczne w kalendarzu.")
        st.markdown('<a href="..." style="color: #007bff; font-weight: bold;">Strona GOV.PL</a>', unsafe_allow_html=True)
    st.divider()
    cal_data = calendar(events=get_dynamic_gov_events(), options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False, "selectable": True}, key="calendar_v50")
    if "eventClick" in cal_data:
        event = cal_data["eventClick"]["event"]
        st.success(f"🔍 **Szczegóły:** {event['extendedProps']['provider']} (Pub: {event['extendedProps']['pub_date']})")

# --- 4. SEKCJA SYSTEM I SOFT (MODUŁ SKANERA) ---
elif choice == "💻 System i Soft":
    st.header("💻 Centrum Zarządzania i Skaner")
    
    # Metryki
    c1, c2, c3 = st.columns(3)
    c1.metric("Dysk C:", "433 GB Wolne")
    c2.metric("Status Systemu:", "Stabilny")
    c3.metric("Ostatni Skan:", datetime.datetime.now().strftime("%d.%m.%Y"))

    st.divider()
    
    # LISTA REFERENCYJNA (To, co CHCEMY mieć)
    target_versions = {
        "Adobe Photoshop": "27.3.1",
        "Java": "8.0.401",
        "Total Commander": "10.0",
        "Microsoft Edge": "145.0",
        "ESET": "17.0",
        "Cyberpunk 2077": "2.1",
        "Steam": "1.0.0"
    }

    st.subheader("📁 Wgraj plik moje_programy.txt")
    uploaded_file = st.file_uploader("Wybierz plik wygenerowany przez PowerShell", type="txt")

    if uploaded_file is not None:
        stringio = uploaded_file.getvalue().decode("utf-16") # PowerShell domyślnie używa UTF-16
        
        results = []
        # Analiza wgranego pliku
        for app, target_ver in target_versions.items():
            found = False
            for line in stringio.splitlines():
                if app.lower() in line.lower():
                    # Próba wyciągnięcia wersji z linii (zakładamy format Name Version)
                    current_ver = re.search(r'(\d+[\d\.]*)', line)
                    current_ver = current_ver.group(1) if current_ver else "Wykryto"
                    
                    status = "✅ OK" if target_ver in current_ver else f"⚠️ Update do {target_ver}"
                    results.append({"Program": app, "Twoja Wersja": current_ver, "Status": status})
                    found = True
                    break
            if not found:
                results.append({"Program": app, "Twoja Wersja": "Nie znaleziono", "Status": "❌ Brak w systemie"})
        
        st.subheader("🔍 Wynik analizy Twojego systemu")
        st.table(results)
    else:
        st.info("💡 Wgraj plik, aby sprawdzić aktualność Adobe, Javy, Antywirusa i Gier.")
        
    st.divider()
    st.subheader("📑 Pełna lista (Ręczna)")
    st.table([
        {"Kategoria": "System", "Program": "Java Runtime Environment", "Wersja": "8u401", "Status": "✅"},
        {"Kategoria": "Zabezpieczenia", "Program": "ESET Endpoint Security", "Wersja": "11.0", "Status": "✅"},
        {"Kategoria": "Gry", "Program": "Cyberpunk 2077 / Wiedźmin 3", "Wersja": "Najnowsza", "Status": "✅"},
        {"Kategoria": "Narzędzia", "Program": "Total Commander UP", "Wersja": "9.2", "Status": "⚠️ Update"}
    ])
