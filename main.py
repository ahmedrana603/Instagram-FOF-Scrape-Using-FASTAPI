from fastapi import FastAPI, Request
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading

app = FastAPI()

def setup_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "ENTER_YOUR_SERVICE_ACCOUNT_JSON_HERE.json", scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("ENTER_YOUR_SHEET_NAME_HERE").sheet1

    sheet.clear()
    sheet.update(range_name="A1:C1", values=[["Follower ID", "No of followers", "Followers of followers"]])
    return sheet

def extract_usernames_from_modal(driver, limit=None):
    elements = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "stories"))]')
    usernames = []
    for el in elements:
        href = el.get_attribute("href")
        if href and "instagram.com/" in href:
            username = href.split("instagram.com/")[-1].split('/')[0]
            if username and username not in usernames:
                usernames.append(username)
                if limit and len(usernames) >= limit:
                    break
    return usernames

def get_followers_count(driver, wait):
    try:
        count_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/followers")]/span')))
        return count_elem.text
    except:
        return "0"

def append_to_sheet(sheet, follower_id, followers_count, followers_str):
    sheet.append_row([follower_id, followers_count, followers_str])

def scrape_instagram_followers(sessionid):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/")
    wait = WebDriverWait(driver, 30)

    driver.add_cookie({
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/',
        'secure': True,
        'httpOnly': True,
        'sameSite': 'Lax'
    })
    driver.refresh()
    time.sleep(5)

    # Profile
    profile_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Profile"]/ancestor::a[@role="link"]')))
    driver.execute_script("arguments[0].click();", profile_btn)
    time.sleep(5)

    # Followers
    followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/followers")]')))
    followers_link.click()
    time.sleep(5)

    my_followers_count_str = get_followers_count(driver, wait)
    try:
        my_followers_count = int(''.join(filter(str.isdigit, my_followers_count_str)))
    except:
        my_followers_count = 0

    print(f"\nYou have {my_followers_count} followers")
    all_follower_urls = []

    followers_modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//div[contains(@class, "x6nl9eh")]')))

    while len(all_follower_urls) < my_followers_count:
        follower_links = driver.find_elements(By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "explore"))]')
        for el in follower_links:
            href = el.get_attribute("href")
            if href and href not in all_follower_urls:
                all_follower_urls.append(href)
                if len(all_follower_urls) >= my_followers_count:
                    break
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_modal)
        time.sleep(2)

    try:
        close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button//*[name()="svg"][@aria-label="Close"]/ancestor::button')))
        close_btn.click()
        time.sleep(2)
    except:
        pass

    sheet = setup_google_sheet()

    for i, url in enumerate(all_follower_urls):
        try:
            print(f"\nVisiting follower {i+1}/{len(all_follower_urls)}: {url}")
            driver.get(url)
            time.sleep(5)

            path_parts = urlparse(driver.current_url).path.strip('/').split('/')
            follower_id = path_parts[0]

            followers_count_str = get_followers_count(driver, wait)
            try:
                followers_count = int(''.join(filter(str.isdigit, followers_count_str)))
            except:
                followers_count = 0

            print(f"{follower_id} has {followers_count} followers")

            follower_followers_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/followers")]')))
            follower_followers_link.click()
            time.sleep(3)

            modal = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="dialog"]//div[contains(@class, "x6nl9eh")]')))
            temp_usernames = []
            previous_count = -1
            max_scrolls = 30
            scroll_attempts = 0

            while len(temp_usernames) < followers_count and scroll_attempts < max_scrolls:
                temp_usernames = extract_usernames_from_modal(driver, limit=followers_count)
                print(f"Scroll {scroll_attempts + 1}: {len(temp_usernames)} / {followers_count}")

                if len(temp_usernames) == previous_count:
                    print("No new followers. Breaking.")
                    break

                previous_count = len(temp_usernames)
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                time.sleep(4)
                scroll_attempts += 1

            followers_str = ", ".join(temp_usernames)
            append_to_sheet(sheet, follower_id, followers_count, followers_str)

            try:
                close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button//*[name()="svg"][@aria-label="Close"]/ancestor::button')))
                close_btn.click()
                time.sleep(2)
            except:
                pass

        except Exception as e:
            print(f"Error: {e}")
            continue

    print("\nDone scraping all followers.")
    driver.quit()

class SessionRequest(BaseModel):
    sessionid: str

@app.post("/scrape/")
async def start_scraping(request: SessionRequest):
    threading.Thread(target=scrape_instagram_followers, args=(request.sessionid,)).start()
    return {"status": "Scraping started"}
