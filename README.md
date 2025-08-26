# 📸 Instagram Followers Scraper (FastAPI + Selenium + Google Sheets)

Automate Instagram followers & followers-of-followers scraping using **FastAPI**, **Selenium**, and **Google Sheets** integration.  
Easily fetch followers data with just an Instagram **session ID** and store everything directly in Google Sheets.  

---

## ✨ Features
- 🔑 **Session ID Authentication** → No username/password required.  
- 🌐 **FastAPI Endpoint** → Start scraping with a simple POST request.  
- 🤖 **Selenium Automation** → Handles login, scrolling, and data extraction.  
- 📊 **Google Sheets Integration** → Data is saved live into Google Sheets.  
- ⚡ **Background Threading** → API responds instantly, scraping continues in background.  
- 📝 Extracted Data Includes:  
  - Follower username  
  - Number of followers  
  - Followers of each follower  

---

## 🛠️ Tech Stack
- **[FastAPI](https://fastapi.tiangolo.com/)** → API framework  
- **[Selenium](https://www.selenium.dev/)** → Web automation & scraping  
- **[Google Sheets API (gspread)](https://docs.gspread.org/)** → Save scraped data  
- **[Threading](https://docs.python.org/3/library/threading.html)** → Background execution  


