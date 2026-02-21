import streamlit as st
import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_calendar import calendar

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="Operations Center PRO", layout="wide")

# --- 2. DANE Z TWOJEJ TABELI (KALENDARZ) ---
def get_gov_planned_events():
    raw_data = [
        ("2026-03-01", "15:00", "20:00", "PPSA"),
        ("2026-02-26", "18:00", "23:00", "PPSA"),
        ("2026-02-18", "18:00", "23:00", "PPSA"),
        ("2026-02-15", "15:00", "20:00", "PPSA"),
        ("2026-02-08", "15:00", "20:00", "PPSA"),
        ("2026-02-03", "12:50", "14:00", "COI"),
        ("2026-02-01", "15:00", "20:00", "PPSA"),
        ("2026-01-30", "22:00", "02:00", "COI"),
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

# --- 3. ZMODYFIKOWANA FUNKCJA SCRAPUJĄCA (TYLKO PRZERWY, BEZ MENU) ---
def get_clean_alerts(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Usuwamy eArchiwum oraz typowe elementy menu/nav
        for tag in soup(['nav', 'header', 'footer', 'script', 'style', 'button', 'form']):
            tag.extract()

        for t in soup.find_all(string=re.compile("earchiwum", re.I)):
            if t.parent: t.parent.extract()
            
        # Szukamy tylko w paragrafach i listach, gdzie tekst jest dłuższy (komunikaty)
        potential_nodes = soup.find_all(['p', 'li', 'div'])
        alerts = []
        
        for node in potential_nodes:
            # Pobieramy tekst bez dzieci, żeby nie powtarzać zagnieżdżonych divów
            text = node.get_text(" ", strip=True)
