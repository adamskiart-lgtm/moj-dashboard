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
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# CSS: Czytelne metryki i mniejsza czcionka tabeli
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700; color: #1E3A8A; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; }
    .stDataFrame { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. [ZAMROŻONE] E-DORĘCZENIA ---
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

# --- 3. NAWIGACJA ---
with st.sidebar:
    st.title("📂 Menu")
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v76")
    st.divider()
    st.write("**Wersja:** v7.6")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    st.info(get_poczta_simple_alert())
    st.divider()
    # Tutaj Twój zamrożony kalendarz (uproszczony w tym widoku dla czytelności kodu)

# --- 4. SYSTEM I SOFT (NAPRAWIONY ODCZYT) ---
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

    st.subheader("1. Wykonaj Raport (PowerShell Admin)")
    final_ps = (
        "powershell -Command \"Write-Output '---HARDWARE---'; "
        "Write-Output ('MODEL:' + (Get-CimInstance Win32_ComputerSystem).Model); "
        "Write-Output ('CPU:' + (Get-CimInstance Win32_Processor).Name); "
        "Write-Output ('RAM:' + [Math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1GB) + ' GB'); "
        "Write-Output ('GPU:' + (Get-CimInstance Win32_VideoController).Name); "
        "Write-Output '---SOFTWARE---'; "
        "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
        "Select-Object DisplayName, DisplayVersion | Out-File C:\\Test\\raport_systemowy.txt -Encoding utf8; exit\""
    )
    st.code(final_ps, language='powershell')

    st.divider()
    up = st.file_uploader("2. Wgraj raport z C:\\Test\\raport_systemowy.txt", type="txt", key="up_v76")

    if up:
        # Odczytujemy plik z wymuszeniem ignorowania błędnych znaków
        raw_text = up.read().decode('utf-8', errors='ignore')
        lines = raw_text.splitlines()
        
        hw = {'Model': 'N/A', 'CPU': 'N/A', 'RAM': 'N/A', 'GPU': 'N/A'}
        
        # Agresywne przeszukiwanie linii pod kątem kluczowych słów
        for line in lines:
            line_clean = line.strip().upper()
            if "MODEL:" in line_clean: hw['Model'] = line.split(':', 1)[1].strip()
            elif "CPU:" in line_clean: hw['CPU'] = line.split(':', 1)[1].strip().split('@')[0]
            elif "RAM:" in line_clean: hw['RAM'] = line.split(':', 1)[1].strip()
            elif "GPU:" in line_clean: hw['GPU'] = line.split(':', 1)[1].strip()

        st.success("✅ Dane wczytane pomyślnie!")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Maszyna", hw['Model'])
        c2.metric("Procesor", hw['CPU'])
        c3.metric("RAM", hw['RAM'])
        c4.metric("Grafika", hw['GPU'])
        
        st.divider()
        
        results, updates = [], []
        for line in lines:
            # Omijamy nagłówki sprzętowe
            if any(x in line.upper() for x in ["---", "MODEL:", "CPU:", "RAM:", "GPU:", "DISPLAYNAME"]): continue
            
            # Podział linii na nazwę i wersję
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 1 and len(parts[0]) > 2:
                name, ver = parts[0], (parts[1] if len(parts) > 1 else "---")
                status = "✅ OK"
                
                for key, meta in app_meta.items():
                    if key.lower() in name.lower():
                        try:
                            # Wyciągamy pierwszą liczbę z wersji do porównania
                            v_num = int(re.search(r'\d+', ver).group())
                            t_num = int(re.search(r'\d+', meta["target"]).group())
                            if v_num < t_num:
                                status = f"⚠️ Update do {meta['target']}"
                                updates.append({"n": name, "u": meta["url"]})
                        except: pass
                results.append({"Program": name, "Wersja": ver, "Status": status})

        if results:
            st.dataframe(pd.DataFrame(results).drop_duplicates().sort_values(by="Program"), use_container_width=True, hide_index=True)
            if updates:
                st.subheader("🚀 Instrukcja Aktualizacji")
                for itm in updates: st.warning(f"**{itm['n']}** ➔ [Pobierz stąd]({itm['u']})")
