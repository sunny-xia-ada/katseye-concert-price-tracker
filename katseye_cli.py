


import time
import random
import threading
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# Optional: Try to import notification, warn if missing
try:
    from plyer import notification
    NOTIFICATIONS_ACTIVE = True
except ImportError:
    NOTIFICATIONS_ACTIVE = False
    print("!! Warning: 'plyer' not found. Desktop notifications disabled. !!")

# --- CONFIGURATION ---
SEATGEEK_CLIENT_ID = "YOUR_SEATGEEK_CLIENT_ID_HERE" 

# Event URLs for Tonight (Dec 9)
URLS = {
    "SeatGeek": f"https://api.seatgeek.com/2/events?q=Katseye&venue.city=Seattle&client_id={SEATGEEK_CLIENT_ID}",
    "VividSeats": "https://www.vividseats.com/katseye-tickets-seattle-wamu-theater---seattle-12-9-2025--concerts-pop/production/5867054",
    "StubHub": "https://www.stubhub.com/katseye-seattle-tickets-12-9-2025/event/158865976/",
}

TARGET_PRICE = 150
AUTO_TRACKING = False

def send_notification(site, price, link):
    msg = f"{site} has a ticket for ${price}!"
    print(f"\n[ALERT] {msg}")
    print(f"Link: {link}\n")
    if NOTIFICATIONS_ACTIVE:
        try:
            notification.notify(
                title=f"TICKET FOUND: ${price}",
                message=msg,
                timeout=10
            )
        except:
            pass

def scrape_vivid(driver):
    try:
        print("   > Checking Vivid Seats...")
        driver.get(URLS['VividSeats'])
        # Wait for price element
        try:
            WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '$')]")))
        except:
            print("   > Vivid Seats: Timeout (Page didn't load price)")
            return

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prices = []
        for span in soup.find_all('span'):
            txt = span.get_text().strip()
            if txt.startswith('$') and len(txt) < 8:
                try:
                    val = int(txt.replace('$','').replace(',',''))
                    prices.append(val)
                except: pass
        
        if prices:
            low = min(prices)
            print(f"   > Vivid Seats Lowest: ${low}")
            if low <= TARGET_PRICE:
                send_notification("Vivid Seats", low, URLS['VividSeats'])
        else:
            print("   > Vivid Seats: No prices found.")
            
    except Exception as e:
        print(f"   > Vivid Error: {e}")

def scrape_stubhub(driver):
    try:
        print("   > Checking StubHub...")
        driver.get(URLS['StubHub'])
        time.sleep(5) # Wait for JS
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        prices = []
        for div in soup.find_all(['div', 'span']):
            txt = div.get_text().strip()
            if txt.startswith('$') and len(txt) < 8:
                try:
                    val = int(txt.replace('$','').replace(',',''))
                    prices.append(val)
                except: pass
        
        valid_prices = [p for p in prices if p > 10]
        if valid_prices:
            low = min(valid_prices)
            print(f"   > StubHub Lowest: ${low}")
            if low <= TARGET_PRICE:
                send_notification("StubHub", low, URLS['StubHub'])
        else:
            print("   > StubHub: No prices found (or blocked).")
            
    except Exception as e:
        print(f"   > StubHub Error: {e}")

def run_check():
    print(f"\n--- Checking Prices (Target: ${TARGET_PRICE}) ---")
    
    # 1. SeatGeek (API)
    try:
        resp = requests.get(URLS['SeatGeek'])
        data = resp.json()
        if 'events' in data and data['events']:
            event = data['events'][0]
            low = event['stats']['lowest_price']
            if low:
                print(f"   > SeatGeek Lowest: ${low}")
                if low <= TARGET_PRICE:
                    send_notification("SeatGeek", low, event['url'])
            else:
                print("   > SeatGeek: No tickets listed.")
    except Exception as e:
        print(f"   > SeatGeek Error: {e}")

    # 2. Browser Check (Vivid/StubHub)
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new') # Uncomment to hide browser, but increases block risk
    
    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        scrape_vivid(driver)
        scrape_stubhub(driver)
    except Exception as e:
        print(f"   > Browser Error: {e}")
    finally:
        if driver:
            driver.quit()
    
    print("--- Check Complete ---\n")

def auto_tracker_loop():
    while AUTO_TRACKING:
        run_check()
        if not AUTO_TRACKING: break
        wait = random.randint(280, 320)
        print(f"[Auto] Sleeping for {wait} seconds...")
        time.sleep(wait)

# --- MAIN MENU ---
if __name__ == "__main__":
    print("=== KATSEYE SEATTLE TICKET TRACKER (CLI) ===")
    print(f"Target Price: ${TARGET_PRICE}")
    
    while True:
        print("Commands:")
        print("  [Enter] Check prices NOW")
        print("  [a]     Start Auto-Tracker (Every 5 mins)")
        print("  [s]     Stop Auto-Tracker")
        print("  [q]     Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == "":
            run_check()
        elif choice == 'a':
            if not AUTO_TRACKING:
                AUTO_TRACKING = True
                print("Starting Auto-Tracker in background...")
                t = threading.Thread(target=auto_tracker_loop)
                t.daemon = True
                t.start()
            else:
                print("Auto-Tracker is already running.")
        elif choice == 's':
            AUTO_TRACKING = False
            print("Auto-Tracker stopping after current cycle.")
        elif choice == 'q':
            print("Exiting.")
            break