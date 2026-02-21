import streamlit as st
import datetime
import imaplib
import email
from email.header import decode_header
import requests
import re

st.set_page_config(page_title="Creative Studio Dashboard", layout="wide")

# --- FUNKCJA POBIERANIA TREŚCI MAILI ---
def get_recent_emails():
    emails_list = []
    try:
        user = st.secrets["GMAIL_USER"]
        password = st.secrets["GMAIL_PASSWORD"]
        
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("inbox")

        # Obliczanie daty sprzed 2 dni w formacie IMAP (np. 19-Feb-2026)
        date_since = (datetime.date.today() - datetime.timedelta(days=2)).strftime("%d-%b-%Y")
        status, response = mail.search(None, f'(SINCE {date_since})')
        
        id_list = response[0].split()
        # Odwracamy listę, żeby najnowsze były na górze, i bierzemy max 10
        for i in reversed(id_list[-10:]):
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Dekodowanie tematu
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Pobieranie krótkiej treści
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    # Skracanie treści i szukanie linków
                    short_body = body[:200].replace('\n', ' ') + "..."
                    links = re.findall(r'(https?://\S+)', body)
                    
                    # Link do otwarcia wiadomości w Gmailu (uproszczony)
                    # Używamy Message-ID do precyzyjnego wyszukania w Gmailu
                    msg_id = msg.get("Message-ID", "")
                    clean_id = msg_id.strip("<>")
                    gmail_link = f"https://mail.google.com/mail/u/0/#search/rfc822msgid%3A{clean_id}"

                    emails_list.append({
                        "subject": subject,
                        "body": short_body,
                        "links": links[:2], # bierzemy max 2 linki z treści
                        "url": gmail_link
                    })
        mail.logout()
        return emails_list
    except Exception as e:
        return f"Błąd: {str(e)}"

# --- UKŁAD STRONY ---
st.title("🚀 Personal Operations Center")
st.write(f"Ostatnia aktualizacja: **{datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}**")
st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("📬 Ostatnie wiadomości (2 dni)")
    emails = get_recent_emails()
    
    if isinstance(emails, list):
        if not emails:
            st.info("Brak nowych wiadomości z ostatnich 2 dni.")
        for m in emails:
            with st.expander(f"✉️ {m['subject']}"):
                st.write(f"**Treść:** {m['body']}")
                if m['links']:
                    st.write("**Linki w treści:**")
                    for link in m['links']:
                        st.write(f"🔗 [Link z maila]({link})")
                st.divider()
                st.link_button("Otwórz tę wiadomość w Gmailu", m['url'])
    else:
        st.error(emails)

    st.divider()
    st.header("⚙️ Listing Oprogramowania")
    # (Tutaj zostaje Twoja tabela softu...)
    st.table([{"Program": "Adobe Photoshop 2026", "Twoja": "27.3.1", "Status": "✅ OK"}])

with col_right:
    # (Tutaj zostaje sekcja Maszyna i Kalendarz...)
    with st.container(border=True):
        st.subheader("💻 Twoja Maszyna")
        st.markdown("**Dell Precision 5540**\ni9-9880H | 32 GB RAM")
    
    st.divider()
    st.subheader("📅 Kalendarz")
    st.write("📌 Sesja produktowa - 25.02")

st.caption("Dashboard v1.6 | Enhanced Mail View")

