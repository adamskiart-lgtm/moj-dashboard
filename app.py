import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v4.9
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- [SEKCJA ZAMROŻONA] 2. KALENDARZ E-DORĘCZENIA ---
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

# --- [SEKCJA ZAMROŻONA] 3. KOMUNIKATY E-DORĘCZENIA ---
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

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v49")
    st.divider()
    st.write(f"**Wersja kodu:** v4.9")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕵️ Poczta Polska")
        st.info(get_poczta_simple_alert())
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color: #007bff; text-decoration: none; font-weight: bold;">Strona Poczty Polskiej - Prace serwisowe</a>', unsafe_allow_html=True)
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Najnowsze ogłoszenia o planowanych przerwach w kalendarzu poniżej.")
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color: #007bff; text-decoration: none; font-weight: bold;">Strona GOV.PL - Niedostępność e-Doręczeń</a>', unsafe_allow_html=True)
    st.divider()
    st.subheader("📅 Harmonogram Planowany")
    cal_data = calendar(events=get_dynamic_gov_events(), options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False, "selectable": True}, key="calendar_v49")
    if "eventClick" in cal_data:
        event = cal_data["eventClick"]["event"]
        st.success(f"🔍 **Szczegóły zdarzenia:**")
        st.write(f"**Podmiot:** {event['extendedProps']['provider']}")
        st.write(f"**Data publikacji na GOV:** {event['extendedProps']['pub_date']}")

# --- 5. NOWA SEKCJA: SYSTEM I SOFT (ROZBUDOWANA) ---
elif choice == "💻 System i Soft":
    st.header("💻 Centrum Zarządzania Systemem")
    
    # Podsumowanie sprzętowe
    st.info("💻 **Specyfikacja jednostki:** Dell Precision 5540 | Intel i9-9880H | 32GB RAM | Quadro T2000")
    
    col_sys1, col_sys2, col_sys3 = st.columns(3)
    col_sys1.metric("Dysk C (System):", "433 GB Wolne", "OK")
    col_sys2.metric("Ostatni Backup:", "21.02.2026", "✅")
    col_sys3.metric("Uptime:", "14h 22m", "Stabilny")
    
    st.divider()
    
    st.subheader("⚙️ Inwentaryzacja Oprogramowania")
    
    # Pełna lista programów
    soft_list = [
        {"Program": "Adobe Photoshop 2026", "Wersja": "27.3.1", "Status": "⚠️ Update dostępny"},
        {"Program": "Adobe Lightroom Classic", "Wersja": "15.1", "Status": "✅ Aktualny"},
        {"Program": "Adobe Premiere Pro", "Wersja": "25.0", "Status": "✅ Aktualny"},
        {"Program": "Microsoft Edge", "Wersja": "145.0.3122.0", "Status": "✅ Aktualny"},
        {"Program": "Total Commander UP", "Wersja": "9.2", "Status": "⚠️ Nowa wersja (10.0)"},
        {"Program": "Visual Studio Code", "Wersja": "1.98.0", "Status": "✅ Aktualny"},
        {"Program": "Python Interpreter", "Wersja": "3.12.2", "Status": "✅ Aktualny"},
        {"Program": "Streamlit Library", "Wersja": "1.32.0", "Status": "⚠️ Update (1.35.0)"}
    ]
    
    st.table(soft_list)
    
    st.divider()
    st.subheader("📝 Notatki Systemowe")
    st.text_area("Pole notatek:", "Sprawdzić spójność bazy danych w poniedziałek rano. Zaktualizować Total Commandera.", height=100)
