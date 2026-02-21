import streamlit as st
import datetime

st.set_page_config(page_title="Creative Studio Dashboard", layout="wide")

# --- NAGŁÓWEK ---
st.title("🚀 Personal Operations Center")
st.write(f"Stan na: **{datetime.date.today().strftime('%d.%m.%Y')}**")

st.divider()

# --- GŁÓWNY UKŁAD (KOLUMNY) ---
# Lewa kolumna (2/3 szerokości) na soft, prawa (1/3) na sprzęt
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("⚙️ Listing Oprogramowania")
    
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"},
        {"Program": "TickTick", "Twoja": "6.4.1", "Najnowsza": "6.4.2", "Status": "ℹ️ Info"}
    ]

    # Wyświetlamy w formie przejrzystej tabeli
    st.table(soft_data)
    
    st.subheader("📬 Powiadomienia ze skrzynek")
    st.info("Trwa konfigurowanie modułu poczty...")

with col_right:
    # Stylizowany kontener dla specyfikacji w prawym górnym rogu
    with st.container(border=True):
        st.subheader("💻 Twoja Maszyna")
        st.markdown(f"""
        **Urządzenie:** Dell Precision 5540  
        **Procesor:** i9-9880H  
        **Pamięć RAM:** 32 GB  
        **Grafika:** Quadro T2000 (4GB)
        """)
        st.progress(0.46, text="Dysk: 433GB wolne")
        st.success("Wydajność: IDEALNA")

    st.subheader("📅 Kalendarz")
    st.write("📌 Dzisiaj: Brak

