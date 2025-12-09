


import time
import sqlite3
import threading
import re
import os
from flask import Flask, render_template, jsonify
from flask_apscheduler import APScheduler
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIG ---
SEATGEEK_CLIENT_ID = "NTQ4NTgzMTl8MTc2NTMwOTQxMC4zMzc1MTQ"
URLS = {
    "SeatGeek_API": f"https://api.seatgeek.com/2/events?q=Katseye&venue.city=Seattle&client_id={SEATGEEK_CLIENT_ID}",
    "VividSeats": "https://www.vividseats.com/katseye-tickets-seattle-wamu-theater---seattle-12-9-2025--concerts-pop/production/5867054?quantity=1&maxPrice=1744&currency=USD",
    "StubHub": "https://www.stubhub.com/katseye-seattle-tickets-12-9-2025/event/158865976/?backUrl=%2Fkatseye-tickets%2Fcategory%2F150357413&quantity=1",
}

app = Flask(__name__)
scheduler = APScheduler()

def init_db():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prices 
                 (id INTEGER PRIMARY KEY, site TEXT, price INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def save_price(site, price):
    print(f"💰 Found {site} price: ${price}")
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute("INSERT INTO prices (site, price) VALUES (?, ?)", (site, price))
    conn.commit()
    conn.close()

def get_price_from_text(soup):
    """Helper to find the lowest number starting with $ in a page"""
    prices = []
    for tag in soup.find_all(['span', 'div', 'b']):
        text = tag.get_text().strip()
        if '$' in text and len(text) < 10:
            # Remove non-digits
            clean = re.sub(r'[^\d]', '', text)
            if clean:
                try:
                    val = int(clean)
                    if val > 20: # Filter out $1 placeholders
                        prices.append(val)
                except: pass
    return min(prices) if prices else None

def run_tracker():
    print("--- 🔄 Running Background Check ---")
    seatgeek_url_to_scrape = None

    # 1. Check SeatGeek API (To get price OR the URL)
    try:
        resp = requests.get(URLS['SeatGeek_API'])
        data = resp.json()
        if 'events' in data and data['events']:
            event = data['events'][0]
            # Try to get price from API
            if event['stats'].get('lowest_price'):
                save_price("SeatGeek", event['stats']['lowest_price'])
            else:
                # If API returns null, grab the URL to scrape it later
                print("SG API has no price. Switching to scrape mode...")
                seatgeek_url_to_scrape = event['url']
    except Exception as e: print(f"SG API Error: {e}")

    # 2. Launch Browser for Scraping
    options = uc.ChromeOptions()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)

        # --- SCRAPE SEATGEEK (Fallback) ---
        if seatgeek_url_to_scrape:
            try:
                driver.get(seatgeek_url_to_scrape)
                time.sleep(4)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                price = get_price_from_text(soup)
                if price: save_price("SeatGeek", price)
            except Exception as e: print(f"SG Scrape Error: {e}")

        # --- SCRAPE VIVID SEATS ---
        try:
            driver.get(URLS['VividSeats'])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '$')]")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = get_price_from_text(soup)
            if price: save_price("Vivid Seats", price)
        except Exception as e: print(f"Vivid Error: {e}")

        # --- SCRAPE STUBHUB ---
        try:
            driver.get(URLS['StubHub'])
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = get_price_from_text(soup)
            if price: save_price("StubHub", price)
        except Exception as e: print(f"StubHub Error: {e}")

    except Exception as e: print(f"Browser Error: {e}")
    finally:
        if driver: driver.quit()
    print("--- ✅ Check Complete ---")

# --- ROUTES ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/data')
def get_data():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    latest = {}
    for site in ["SeatGeek", "Vivid Seats", "StubHub"]:
        c.execute("SELECT price FROM prices WHERE site=? ORDER BY timestamp DESC LIMIT 1", (site,))
        res = c.fetchone()
        latest[site] = res[0] if res else "N/A"
    
    # Get last 50 data points for chart
    c.execute("SELECT site, price, timestamp FROM prices ORDER BY timestamp ASC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    return jsonify({'latest': latest, 'history': rows})

@app.route('/api/scan')
def trigger_scan():
    threading.Thread(target=run_tracker).start()
    return jsonify({'status': 'Scan started'})

if __name__ == '__main__':
    init_db()
    # PREVENT DOUBLE RUN: Only start scheduler if not already running
    if not scheduler.running:
        scheduler.add_job(id='Scheduled Task', func=run_tracker, trigger="interval", minutes=5)
        scheduler.start()
    
    # DISABLE RELOADER to prevent double-execution
    app.run(debug=True, port=5000, use_reloader=False)