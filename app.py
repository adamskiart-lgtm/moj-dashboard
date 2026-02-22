import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import shutil
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
# Wersja kodu: v6.5 [2026-02-22]
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- [ZAMROŻONE] 2. SEKACJA E-DORĘCZENIA ---
# (Pozostaje nienaruszona zgodnie z v6.4)
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
    choice = st.radio("Nawigacja:", ["📡 e-Doręczenia", "💻 System i Soft"], key="nav_v65")
    st.divider()
    st.write("**Wersja:** v6.5")

if choice == "📡 e-Doręczenia":
    st.header("📡 Monitor e-Doręczeń")
    st.info(get_poczta_simple_alert())
    st.markdown('[➔ Strona Poczty Polskiej](https://edoreczenia.poczta-polska.pl/informacje/prace-serwisowe/)')
    st.divider()
    # (Reszta widoku e-doręczeń bez zmian)

# --- 4. WIDOK: SYSTEM I SOFT (AUTO-SPECS) ---
elif choice == "💻 System i Soft":
    st.header("💻 Audyt Sprzętowo-Programowy")
    
    st.subheader("1. Przygotuj raport zbiorczy")
    st.write("Wklej w PowerShell (Admin):")
    st.code('$info = @{Model=(Get-CimInstance Win32_ComputerSystem).Model; CPU=(Get-CimInstance Win32_Processor).Name; RAM="$([Math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB)) GB"; GPU=(Get-CimInstance Win32_VideoController).Name}; $info | Out-File "C:\\Test\\raport_systemowy.txt"; Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Out-File "C:\\Test\\raport_systemowy.txt" -Append', language='powershell')

    st.divider()
    up = st.file_uploader("Wgraj plik raport_systemowy.txt z C:\\Test\\", type="txt", key="up_v65")

    if up:
        raw = up.read()
        try: text = raw.decode('utf-16')
        except: text = raw.decode('utf-8')

        # Wyciąganie specyfikacji z pliku
        spec_model = re.search(r'Model\s+=\s+(.*)', text)
        spec_cpu = re.search(r'CPU\s+=\s+(.*)', text)
        spec_ram = re.search(r'RAM\s+=\s+(.*)', text)
        spec_gpu = re.search(r'GPU\s+=\s+(.*)', text)

        if spec_model:
            st.info(f"💻 **Wykryta Jednostka:** {spec_model.group(1)} | {spec_cpu.group(1) if spec_cpu else 'N/A'}")
            st.write(f"🚀 **Zasoby:** RAM: {spec_ram.group(1) if spec_ram else 'N/A'} | GPU: {spec_gpu.group(1) if spec_gpu else 'N/A'}")
        
        # Miejsce na dysku (pobierane lokalnie przez serwer lub info o potrzebie stałego monitoringu)
        total, used, free = shutil.disk_usage("C:")
        st.metric("Wolne miejsce na C (Serwer/Lokalnie):", f"{free // (2**30)} GB")

        # Analiza oprogramowania (Baza wersji z v6.3)
        app_meta = {"Adobe": "27.0", "Norton": "22.0", "Epic": "15.0", "Fortnite": "28.0", "Java": "8.0", "Edge": "140"}
        results = []
        for line in text.splitlines():
            if line.strip() and "=" not in line and "DisplayName" not in line:
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 1:
                    name, ver = parts[0], (parts[1] if len(parts) > 1 else "---")
                    status = "✅ OK"
                    for key, target_v in app_meta.items():
                        if key.lower() in name.lower():
                            try:
                                if float(ver.split('.')[0]) < float(target_v.split('.')[0]):
                                    status = f"⚠️ Update do {target_v}"
                            except: pass
                    results.append({"Program": name, "Wersja": ver, "Status": status})
        
        if results:
            df = pd.DataFrame(results).drop_duplicates().sort_values(by="Program")
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("Czekam na raport_systemowy.txt...")
