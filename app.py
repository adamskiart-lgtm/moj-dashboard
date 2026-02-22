import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v4.2
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. KALENDARZ (KOD ZAMROŻONY) ---
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
            if len(cols) >= 2:
                raw_dt = cols[0].get_text().strip().lower()
                podmiot = cols[1].get_text().strip()
                try:
                    day = re.search(r'(\d{1,2})', raw_dt).group(1).zfill(2)
                    month = months[next(m for m in months if m in raw_dt)]
                    year = re.search(r'(202\d)', raw_dt).group(1)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', raw_dt)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Planowana"
                    iso_date = f"{year}-{month}-{day}"
                    event_id = f"{iso_date}_{podmiot}"
                    if not any(e.get('id') == event_id for e in events):
                        events.append({"id": event_id, "title": f"{time_range} | Zgłosił: {podmiot}", "start": iso_date, "end": iso_date, "backgroundColor": "#EE6C4D" if "PP" in podmiot else "#3D5A80", "display": "block", "allDay": True})
                except: continue
        return events
    except: return []

# --- 3. DYNAMICZNY KOMUNIKAT POCZTY (NAPRAWIONY) ---
def get_poczta_dynamic_alert():
    try:
        url = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
        # Używamy bardziej zaawansowanych nagłówków, by strona nas nie blokowała
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Szukamy tekstu wewnątrz głównej sekcji treści strony
        main_content = soup.find('main') or soup.find('article') or soup.body
        all_text = main_content.get_text("\n", strip=True)
        
        # Szukamy początku komunikatu: od "Informujemy"
        # i końca: do daty publikacji (format XX.XX.XXXX)
        pattern = re.compile(r"(Informujemy.*?\d{2}\.\d{2}\.\d{4})", re.DOTALL | re.IGNORECASE)
        match = pattern.search(all_text)
        
        if match:
            return match.group(1)
        else:
            # Rezerwowy sposób: jeśli nie znajdziemy "Informujemy", bierzemy pierwszy akapit z datą
            for p in soup.find_all(['p', 'div']):
                txt = p.get_text().strip()
                if "2026" in txt and len(txt) > 50:
                    return txt
            return "Nie udało się sparsować najnowszego komunikatu. Sprawdź stronę bezpośrednio."
    except Exception as e:
        return f"Błąd połączenia: {str(e)}"

# --- 4. INTERFEJS ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.write("**Wersja kodu:** v4.2")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    
    col1, col2 = st.columns(2)
    
    # SEKCJA POCZTA POLSKA
    with col1:
        st.subheader("🕵️ Poczta Polska")
        # Wyświetlanie dynamiczne
        alert_body = get_poczta_dynamic_alert()
        st.error(alert_body) # Wyświetlamy w czerwonym boksie dla widoczności
        
        # Link jako niebieska nazwa (Markdown)
        st.markdown('<a href="https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/" style="color: #007bff; text-decoration: none; font-weight: bold;">Strona Poczty Polskiej - Prace serwisowe</a>', unsafe_allow_html=True)

    # SEKCJA GOV.PL
    with col2:
        st.subheader("🕵️ GOV.PL")
        st.warning("Najnowsze informacje o przerwach w tabeli poniżej.")
        
        # Link jako niebieska nazwa (Markdown)
        st.markdown('<a href="https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen" style="color: #007bff; text-decoration: none; font-weight: bold;">Strona GOV.PL - Niedostępność e-Doręczeń</a>', unsafe_allow_html=True)

    st.divider()
    
    # KALENDARZ (ZAMROŻONY)
    st.subheader("📅 Harmonogram (Zgłoszenia PP / COI)")
    calendar(events=get_dynamic_gov_events(), options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth", "height": 450, "locale": "pl", "displayEventTime": False
    })

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.table([{"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"}, {"Program": "Microsoft Edge", "Status": "✅ OK"}])
