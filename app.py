import streamlit as st
import datetime
import imaplib
import email
from email.header import decode_header
import requests

st.set_page_config(page_title="Creative Studio Dashboard", layout="wide")

# --- FUNKCJA POBIERANIA TEMATÓW I LINKÓW ---
def get_email_links():
    links_data = []
    try:
        user = st.secrets["GMAIL_USER"]
        password = st.secrets["GMAIL_PASSWORD"]
        
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("inbox")

        # Szukamy wiadomości z ostatnich 2 dni
        date_since = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%d-%b-%Y")
        status, response = mail.search(None, f'(SINCE {date_since})')
        
        id_list = response[0].split()
        for i in reversed(id_list[-10:]): # Max 10 najnowszych
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Generowanie linku na podstawie Message-ID
                    msg_id = msg.get("Message-ID", "").strip("<>")
                    gmail_link = f"https://mail.google.com/mail/u/0/#search/rfc822msgid%3A{msg_id}"
                    
                    links_data.append({"subject": subject, "url": gmail_link})
        mail.logout()
        return links_data
    except:
        return []

# --- UKŁAD STRONY ---
st.title("🚀 Personal Operations Center")
st.write(f"Stan na: **{datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}**")
st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    # 1. LISTA OPROGRAMOWANIA
    st.header("⚙️ Status Oprogramowania")
    soft_data = [
        {"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Najnowsza": "27.4.0", "Status": "⚠️ Update"},
        {"Program": "Adobe Lightroom Classic", "Twoja": "15.1", "Najnowsza": "15.1", "Status": "✅ OK"},
        {"Program": "Microsoft Edge", "Twoja": "145.0", "Najnowsza": "145.0", "Status": "✅ OK"},
        {"Program": "Total Commander UP", "Twoja": "9.2", "Najnowsza": "9.3", "Status": "⚠️ Nowa wersja"},
        {"Program": "TickTick", "Twoja": "6.4.1", "Najnowsza": "6.4.2", "Status": "ℹ️ Info"}
    ]
    st.table(soft_data)
    
    st.divider()
    
    # 2. LISTA WIADOMOŚCI (Same linki)
    st.header("📬 Ostatnie tematy wiadomości")
    email_links = get_email_links()
    
    if email_links:
        for m in email_links:
            # Każdy temat jest teraz klikalnym linkiem
            st.markdown(f"🔗 [{m['subject']}]({m['url']})")
    else:
        st.info("Brak nowych wiadomości w ostatnich 2 dniach.")

with col_right:
    # PRAWY PANEL (Maszyna i Kalendarz)
    with st.container(border=True):
        st.subheader("💻 Twoja Maszyna")
        st.markdown(f"**Dell Precision 5540**\n\n**CPU:** i9-9880H\n\n**RAM:** 32 GB\n\n**GPU:** T2000")
        st.progress(0.46, text="Dysk: 433GB wolne")

    st.divider()
    
    st.subheader("📅 Kalendarz")
    # Tutaj funkcja kalendarza, którą dodałeś wcześniej
    st.write("📌 Sprawdź nadchodzące sesje w Google Calendar")

st.divider()
st.caption("Dashboard v1.7 | Streamlined View")

