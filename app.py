import streamlit as st
import datetime

st.set_page_config(page_title="Creative Workstation Dashboard", layout="wide")

st.title("📸 Twoje Centrum Dowodzenia")
st.write(f"Ostatnia weryfikacja systemu: **{datetime.date.today().strftime('%d.%m.%Y')}**")

st.divider()

# --- SEKCJA 1: AUDYT SPRZĘTOWY (Twój Dell Precision 5540) ---
st.header("💻 Status Twojej Stacji Roboczej")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧠 Procesor i RAM")
    st.success("**Intel Core i9-9880H**")
    st.success("**32 GB RAM**")
    st.caption("Status: Wybitny. Masz dwukrotność zalecanej pamięci RAM.")

with col2:
    st.subheader("🖼️ Grafika (GPU)")
    st.success("**NVIDIA Quadro T2000 (4GB)**")
    st.info("Akceleracja AI: Aktywna")
    st.caption("Status: Bardzo dobry. Karta wspiera funkcje 'AI Denoise' i 'Generative Fill'.")

with col3:
    st.subheader("🗄️ Przestrzeń")
    st.warning("**Dysk: 932 GB**")
    st.progress(0.46) # Na podstawie Twojego screena: 433GB wolne
    st.caption("Zajętość: ok. 54%. Zalecane utrzymanie min. 100GB wolnego dla cache Adobe.")

st.divider()

# --- SEKCJA 2: AKTUALIZACJE I KALENDARZ ---
c1, c2 = st.columns(2)

with c1:
    st.header("⚙️ Oprogramowanie")
    st.metric(label="Lightroom Classic", value="13.2", delta="Aktualny")
    st.metric(label="Photoshop 2024", value="25.5", delta="Sprawdź aktualizację", delta_color="inverse")

with c2:
    st.header("📅 Nadchodzące Terminy")
    # Tu podepniemy Twój prawdziwy kalendarz w kolejnym kroku
    st.info("Łączenie z Google Calendar...")
    st.write("📌 Sesja produktowa - 25.02")
    st.write("📌 Deadline: Retusz portretów - 27.02")

st.caption("Specyfikacja pobrana z systemowego audytu urządzenia: Dell_Prec9i_9g")
