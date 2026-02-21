import streamlit as st
import datetime
import imaplib
import requests

# Konfiguracja strony
st.set_page_config(page_title="Creative Studio Dashboard", layout="wide")

# --- FUNKCJE POMOCNICZE ---

def get_unread_gmail():
    try:
        user = st.secrets["GMAIL_USER"]
        password = st.secrets["GMAIL_PASSWORD"]
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("inbox")
        status, response = mail.search(None, 'UNSEEN')
        count = len(response[0].split())
        mail.logout()
        return count
    except:
        return "Błąd"

def get_calendar_events():
    try:
        api_key = st.secrets["GOOGLE_CALENDAR_API_KEY"]
        calendar_id = st.secrets["GOOGLE_CALENDAR_ID"]
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?key={api_key}&timeMin={now}&maxResults=5&singleEvents=True&orderBy=startTime"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('items', [])
        return None
    except:
        return None

# --- UKŁAD STRONY ---

st.title("🚀 Personal Operations Center")
st.write(f"Ostatnia aktualizacja: **{datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}**")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("⚙️ Listing Oprogramowania")
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"},
        {"Program": "TickTick", "Twoja": "6.4.1", "Najnowsza": "6.4.2", "Status
