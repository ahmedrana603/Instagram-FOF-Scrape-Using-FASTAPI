# Facebook Friends Scraper with Google Sheets Integration

This Python script logs into Facebook using Selenium, scrapes your own friends list and their friends (friends-of-friends), and stores the data in a Google Sheet.

## 🚀 Features

- Logs into Facebook automatically
- Scrapes your friend list and their friend counts
- Extracts names of friends-of-friends
- Saves the data to Google Sheets in real-time

## ⚠️ Disclaimer

- This script automates Facebook, which may violate [Facebook's Terms of Service](https://www.facebook.com/legal/terms). Use at your own risk.
- It is intended for **educational purposes only**.
- Do not use this for spamming or unethical data harvesting.

## 📦 Requirements

- Python 3.7+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)
- A Google Service Account JSON credentials file
- A Google Sheet (shared with the service account email)

## 🔧 Setup

1. **Install dependencies**

```bash
pip install -r requirements.txt
