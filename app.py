import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. AUTOMATYCZNE POBIERANIE DAT Z GOV.PL DO KALENDARZA ---
def get_dynamic_gov_events():
    url = "https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen"
    events = []
    months = {
        'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
        'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
        'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
    }
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Przeszukujemy wiersze tabeli i akapity
        content = soup.find_all(['tr', 'p', 'td'])
        
        for node in content:
            text = node.get_text().strip().lower()
            # Szukamy wzorca zawierającego miesiąc i słowo "godzina"
            if "godz" in text and any(m in text for m in months):
                try:
                    # Wyciąganie dnia
                    day_match = re.search(r'(\d{1,2})', text)
                    if not day_match: continue
                    day = day_match.group(1).zfill(2)
                    
                    # Wyciąganie miesiąca
                    month_name = next(m for m in months if m in text)
                    month = months[month_name]
                    
                    # Wyciąganie roku
                    year_match = re.search(r'(202\d)', text)
                    year = year_match.group(1) if year_match else str(datetime.datetime.now().year)
                    
                    # Wyciąganie godzin (format HH:MM)
                    times = re.findall(r'(\d{1,2}[:.]\d{2})', text)
                    time_range = f"{times[0]}-{times[1]}" if len(times) >= 2 else "Brak godz."
                    
                    iso_date = f"{year}-{month}-{day}"
                    
                    # Sprawdzamy czy data już nie jest na liście, żeby nie dublować
                    if not any(e['start'] == iso_date and time_range in e['title'] for e in events):
                        events.append({
                            "title": f"{time_range} | GOV",
                            "start": iso_date,
                            "end": iso_date,
                            "backgroundColor": "#EE6C4D",
                            "display": "block",
                            "allDay": True # Kluczowe: usuwa systemowe godziny z widoku
                        })
                except:
                    continue
        return events
    except:
        return []

# --- 3. POBIERANIE PEŁNYCH KOMUNIKATÓW (POCZTA I GOV) ---
def get_latest_full_alert(url, keywords, is_poczta=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Czyszczenie kodu ze zbędnych elementów
        for t in soup(['nav', 'header', 'footer', 'script', 'style', 'button', 'form']):
            t.extract()
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()

        if is_poczta:
            # Poczta Polska: bierzemy cały kontener komunikatu
            content_block = soup.find('div', {'class': 'entry-content'}) or soup.find('article')
            if content_block:
                full_text = content_block.get_text("\n", strip=True)
                # Tniemy dokładnie na dacie publikacji (czerwona linia)
                split_at = re.search(r'\d{2}\.\d{2}\.\d{4}', full_text)
                if split_at:
                    return full_text[:split_at.end()]
                return full_text
        
        # GOV.PL i inne: szukamy pierwszego merytorycznego bloku
        nodes = soup.find_all(['p', 'div', 'li'])
        for node in nodes:
            text = node.get_text(" ", strip=True)
            if any(w in text.lower() for w in keywords) and len(text) > 80:
                return text
        return None
    except:
        return "Błąd połączenia ze stroną."

# --- 4. PASEK BOCZNY ---
with st.sidebar:
    st.title("📂 Panel Sterowania")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.info(f"Ostatnia aktualizacja:\n{datetime.datetime.now().strftime('%H:%M:%S')}")
    st.caption("v3.5 | Autonomous System")

# --- 5. LOGIKA WYŚWIETLANIA ---

if choice == "📡 e-Doręczenia":
    st.header("📡 Dynamiczny Monitor e-Doręczeń")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕵️ Poczta Polska")
        alert_pp = get_latest_full_alert("https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/", ["przerwa", "techniczna", "awaria", "utrudnienia"], is_poczta=True)
        if alert_pp:
            st.error(alert_pp)
        else:
            st.success("✅ Brak nowych komunikatów o przerwach.")

    with col2:
        st.subheader("🕵️ GOV.PL")
        alert_gov = get_latest_full_alert("https://www.gov.pl/web/e-doreczenia/niedostepnosc-uslugi-edoreczen", ["niedostępność", "planowana", "przerwa"])
        if alert_gov:
            st.warning(alert_gov)
        else:
            st.success("✅ Brak nowych komunikatów o przerwach.")

    st.divider()

    # AUTOMATYCZNY KALENDARZ NA DOLE
    st.subheader("📅 Harmonogram Planowany (Pobierany automatycznie z GOV)")
    
    calendar_events = get_dynamic_gov_events()
    
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth",
        "height": 500,
        "locale": "pl",
        "displayEventTime": False # Usuwa pogrubione godziny systemowe
    }
    
    calendar(events=calendar_events, options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Specyfikacja: Dell Precision 5540 | i9-9880H | 32GB RAM")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Dysk C:", "433 GB Wolne", "OK")
    with col_b:
        st.metric("Status Systemu", "Stabilny", "100%")
        
    st.divider()
    st.subheader("⚙️ Status Oprogramowania")
    st.table([
        {"Program": "Adobe Photoshop 2026", "Twoja Wersja": "27.3.1", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja Wersja": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja Wersja": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja Wersja": "9.2", "Status": "⚠️ Nowa wersja"}
    ])

# --- STOPKA ---
st.sidebar.caption("artur.adamski@agroapp.com.pl")
