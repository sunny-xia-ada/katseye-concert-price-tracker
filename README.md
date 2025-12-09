

# 🎫 Katseye Ticket Tracker

A real-time ticket price monitoring dashboard built with **Python (Flask)** and **Selenium**. This tool tracks resale ticket prices across **Ticketmaster, StubHub, Vivid Seats, and SeatGeek** to help users find the best deals for sold-out events.

![Project Status](https://img.shields.io/badge/Status-Active-green)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## ✨ Key Features

* **Hybrid Data Collection:** Uses **Official APIs** (SeatGeek) combined with **Web Scraping** (StubHub, Vivid Seats) to gather data from sources that don't offer public APIs.
* **Anti-Bot Evasion:** Implements `undetected-chromedriver` and randomized user-agent rotation to bypass strict anti-scraping measures (Datadome/Imperva).
* **Real-Time Dashboard:** A responsive, Dark Mode UI built with **Tailwind CSS**.
* **Price Analytics:** Interactive history chart using **Chart.js** to visualize price trends over the last 24 hours.
* **Deal Highlighting:** Automatically flags tickets below a user-defined "Target Price" with visual cues (Green Glow + "DEAL" badges).
* **Background Scheduler:** Uses `APScheduler` to run non-blocking price checks in the background without freezing the UI.

## 🛠️ Tech Stack

* **Backend:** Python, Flask, SQLite, APScheduler
* **Scraping:** Selenium, Undetected-Chromedriver, BeautifulSoup4, RegEx
* **Frontend:** HTML5, Tailwind CSS, Chart.js, JavaScript (Fetch API)

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+
* Google Chrome installed

### Install Dependencies
pip install -r requirements.txt 

### Configure SeatGeek API
Get a free Client ID from the SeatGeek Developer Portal.

Open app.py and replace the placeholder:
SEATGEEK_CLIENT_ID = "YOUR_CLIENT_ID_HERE" 

### Run the Application
python app.py 

### Access the dashboard at: http://127.0.0.1:5000

## ⚙️ How It Works
* API Check: The app first queries the SeatGeek API. If the API returns "null" (common on event day), it seamlessly falls back to scraping the SeatGeek website.

* Scraping: It launches a controlled Chrome instance to parse prices from StubHub and Vivid Seats.

* Data Cleaning: It uses Regex (re) to strip currency symbols and fees, ensuring accurate integer math for price comparisons.

* Database: Prices are stored in a local tickets.db SQLite database to generate historical charts.

## ⚠️ Disclaimer
This project is for educational purposes only. Automated scraping of ticket marketplaces may violate their Terms of Service. Use responsibly and do not use high-frequency request rates that could overload their servers.

## 🔮 Future Improvements
[ ] Add email/SMS notifications using Twilio or SMTP.

[ ] Allow users to change the Target Price directly from the UI.

[ ] Dockerize the application for easier deployment.
