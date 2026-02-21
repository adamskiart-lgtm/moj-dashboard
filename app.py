import streamlit as st
import datetime

# Konfiguracja strony pod monitor Dell Precision
st.set_page_config(page_title="Personal Operations Center", layout="wide")

# --- NAGŁÓWEK ---
st.title("🚀 Personal Operations Center")
st.write(f"Stan na: **{datetime.date.today().strftime('%d.%m.%Y')}**")

st.divider()

# --- GŁÓWNY UKŁAD (KOLUMNY) ---
# col_left (2/3 szerokości) na soft, col_right (1/3) na Twojego Della
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("⚙️ Listing Oprogramowania")
    
    # Dane pobrane z Twojego skanu CMD
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"},
        {"Program": "TickTick", "Twoja": "6.4.1", "Najnowsza": "6.4.2", "Status": "ℹ️ Info"}
    ]

    st.table(soft_data)
    
    st.divider()
    st.header("📬 Podsumowanie skrzynek")
    # Tu przygotujemy grunt pod Gmaila
    st.info("Trwa konfigurowanie bezpiecznego połączenia z pocztą...")

with col_right:
    # Stylizowany kontener specyfikacji - PRAWY GÓRNY RÓG
    with st.container(border=True):
        st.subheader("💻 Twoja Maszyna")
        st.markdown(f"""
        **Urządzenie:** Dell Precision 5540  
        **Procesor:** i9-9880H (8 rdzeni)  
        **Pamięć RAM:** 32 GB  
        **Grafika:** NVIDIA Quadro T2000
        """)
        st.progress(0.46, text="Dysk: 433GB wolne z 932GB")
        st.success("Wydajność: ZALECANA DO LR/PS 2026")

    st.divider()
    st.subheader("📅 Nadchodzące terminy")
    st.write("📌 Dzisiaj: Brak pilnych sesji")
    st.caption("Synchronizacja z Google Calendar i TickTick w toku...")
    st.date_input("Podgląd kalendarza", datetime.date.today(), label_visibility="collapsed")

st.divider()
st.caption("Dashboard adamskiart-lgtm | v1.3 | Fixed SyntaxError")
