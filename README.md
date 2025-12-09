

# 🎫 Katseye Ticket Tracker

A real-time ticket price monitoring dashboard built with **Python (Flask)** and **Selenium**. This tool tracks resale ticket prices across **StubHub, Vivid Seats, and SeatGeek** to help users find the best deals for sold-out events.

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

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/katseye-ticket-tracker.git](https://github.com/YOUR_USERNAME/katseye-ticket-tracker.git)
cd katseye-ticket-tracker
