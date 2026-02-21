import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DANE DO KALENDARZA (PLANOWANE) ---
def get_gov_planned_events():
    raw_data = [
        ("2026-03-01", "15:00", "20:00", "PPSA"),
        ("2026-02-26", "18:00", "23:00", "PPSA"),
        ("2026-02-18", "18:00", "23:00", "PPSA"),
        ("2026-02-15", "15:00", "20:00", "PPSA"),
        ("2026-02-08", "15:00", "20:00", "PPSA"),
    ]
    events = []
    for d, s, e, p in raw_data:
        events.append({
            "title": f"{s}-{e} | {p}",
            "start": f"{d}T{s}:00",
            "end": f"{d}T{e}:00",
            "backgroundColor": "#EE6C4D",
            "display": "block"
        })
    return events

# --- 3. PRECYZYJNE POBIERANIE KOMUNIKATU (DO CZERWONEJ LINII) ---
def get_poczta_clean_alert(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. Usuwamy eArchiwum i menu
        for t in soup(['nav', 'header', 'footer', 'script', 'style']):
            t.extract()
        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()

        # 2. Szukamy głównego kontenera treści (na Poczcie to zazwyczaj .entry-content lub artykuł)
        content = soup.find('div', {'class': 'entry-content'}) or soup.find('article') or soup.body
        
        # 3. Pobieramy cały tekst i szukamy daty publikacji, która kończy komunikat przed linią
        full_text = content.get_text("\n", strip=True)
        
        # Szukamy wzorca daty na końcu komunikatu (np. 20.02.2026)
        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', full_text)
        
        if date_match:
            # Ucinamy tekst zaraz po znalezionej dacie publikacji
            clean_text = full_text[:date_match.end()]
            # Wszystko co zostało pod spodem trafia do archiwum (opcjonalnie)
            archive_text = full_text[date_match.end():].strip()
        else:
            clean_text = full_text
            archive_text = ""

        # Sprawdzamy, czy w czystym tekście są nasze słowa kluczowe
        if any(w in clean_text.lower() for w in keywords):
            return clean_text, archive_text
        return None, ""
    except:
        return "Błąd połączenia.", ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"])
    st.divider()
    st.caption("v3.2 | Red Line Precision")

# --- 5. WIDOKI ---
if choice == "📡 e-Doręczenia":
    st.header("📡 Monitoring e-Doręczeń")
    
    # POCZTA POLSKA - PRECYZYJNY WIDOK
    url_pp = "https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/"
    latest_pp, archive_pp = get_poczta_clean_alert(url_pp, ["przerwa", "techniczna", "utrudnienia", "awaria"])
    
    with st.container(border=True):
        st.subheader("🕵️ Poczta Polska (Ostatni Komunikat)")
        if latest_pp:
            st.error("**PEŁNA TREŚĆ KOMUNIKATU:**")
            st.write(latest_pp)
            
            if archive_pp and len(archive_pp) > 50:
                with st.expander("📁 Pokaż pozostałe dane ze strony"):
                    st.write(archive_pp)
        else:
            st.success("✅ Brak aktywnych komunikatów o przerwach.")

    st.divider()

    # GOV.PL - KLASYCZNY WIDOK
    # (Tutaj zostawiamy poprzednią logikę, bo GOV ma inną strukturę)
    
    # KALENDARZ NA DOLE
    st.subheader("📅 Harmonogram Planowany")
    all_events = get_gov_planned_events()
    calendar_options = {
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
        "initialView": "dayGridMonth",
        "height": 450,
        "locale": "pl"
    }
    calendar(events=all_events, options=calendar_options)

elif choice == "💻 System i Soft":
    st.header("💻 Centrum Systemowe")
    st.info("Dell Precision 5540 | i9 | 32GB RAM")
    st.table([
        {"Program": "Adobe Photoshop 2026", "Status": "⚠️ Update"},
        {"Program": "Microsoft Edge", "Status": "✅ OK"}
    ])
