import streamlit as st
import datetime

# Konfiguracja strony
st.set_page_config(page_title="Mój Dashboard Kreatywny", layout="wide")

# Nagłówek
st.title("📸 Twoje Centrum Dowodzenia")
st.write(f"Dzisiaj jest: **{datetime.date.today().strftime('%d.%m.%Y')}**")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("⚙️ Aktualizacje Programów")
    
    # Sekcja Adobe Lightroom
    st.subheader("Adobe Lightroom Classic")
    # Te dane docelowo będziemy pobierać automatycznie
    st.metric(label="Aktualna wersja", value="13.2", delta="Nowa wersja dostępna!")
    
    with st.expander("Co nowego w Lightroom?"):
        st.write("- **AI Denoise:** Poprawiona redukcja szumów dla plików RAW.")
        st.write("- **Point Color:** Precyzyjna kontrola nad nasyceniem i odcieniem.")
        st.write("- Wsparcie dla najnowszych aparatów i obiektywów.")

with col2:
    st.header("📅 Twój Kalendarz")
    # Miejsce na integrację z Google Calendar
    st.info("Tutaj pojawią się Twoje nadchodzące sesje i spotkania.")
    st.date_input("Podgląd kalendarza", datetime.date.today())

st.divider()
st.caption("Dashboard v1.1 | Monitorowanie Adobe Lightroom")
