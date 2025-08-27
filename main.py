from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\ahmed\Downloads\YOUR JSON FILE", scope)
client = gspread.authorize(creds)
sheet = client.open("fb-sheet").sheet1
sheet.clear()

options = Options()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

driver.get("https://www.facebook.com/")

login_username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Email address or phone number"]')))
login_username.send_keys("ENTER YOUR ID")

login_password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Password"]')))
login_password.send_keys("ENTER YOUR PASSWORD")

login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Log in")]')))
login_button.click()

time.sleep(20)  

wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="navigation"]')))
time.sleep(5)

friends_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Friends"]/ancestor::a[1]')))
friends_button.click()
time.sleep(5)

all_friends_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="All friends"]/ancestor::a[1]')))
all_friends_button.click()
time.sleep(5)

friends_count_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//h2//span[contains(text(), "friend")]')))
digits_only = ''.join(filter(str.isdigit, friends_count_elem.text.strip()))
my_friends_count = int(digits_only) if digits_only else 0
print(f" Total Friends: {my_friends_count}")

friend_name_spans = driver.find_elements(By.XPATH, '//span[contains(@class, "x193iq5w") and text()]')
friend_names = [f.text.strip() for f in friend_name_spans if f.text.strip()]
unique_friend_names = list(set(friend_names))

if not unique_friend_names:
    print(" No friends found.")
    driver.quit()
    exit()

def scroll_to_bottom():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

for idx, target_name in enumerate(unique_friend_names):
    print(f"\n Processing friend {idx+1}/{len(unique_friend_names)}: {target_name}")

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    try:
        friend_link = wait.until(EC.element_to_be_clickable((
            By.XPATH, f'//a[.//span[normalize-space(text())="{target_name}"]]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", friend_link)
        time.sleep(1)
        friend_link.click()
    except Exception as e:
        print(f" Could not click friend {target_name}, skipping. Error: {e}")
        continue

    try:
        temp_count_elem = wait.until(EC.presence_of_element_located((
            By.XPATH, '//a[contains(@href, "sk=friends")]//strong[contains(@class, "x1vvkbs")]'
        )))
        temp_friends_count = temp_count_elem.text.strip()
        print(f" {target_name} has {temp_friends_count} friends")
    except Exception as e:
        print(f" Could not get friend count for {target_name}: {e}")
        temp_friends_count = "N/A"

    try:
        friends_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "friends")]')))
        friends_link.click()
    except Exception as e:
        print(f" Could not click friends link for {target_name}: {e}")

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="main"]')))
        scroll_to_bottom()
        print(" Scrolling done — all friends loaded.")
    except Exception as e:
        print(f" Error during scrolling for {target_name}: {e}")

    friend_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "facebook.com") and @role="link"]//span')
    fof_names = []
    for el in friend_elements:
        try:
            name = el.text.strip()
            if name and len(name.split()) >= 2 and name not in fof_names:
                fof_names.append(name)
        except:
            continue

    fof_combined = ",".join(fof_names)

    try:
        sheet.append_row([target_name, temp_friends_count, fof_combined])
        print(f" Saved friends-of-friends for {target_name} to sheet.")
    except Exception as e:
        print(f" Could not append to sheet for {target_name}: {e}")

    try:
        friends_nav = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/friends/"]')))
        friends_nav.click()

        wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="All friends"]')))
        all_friends_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="All friends"]/ancestor::a[1]')))
        all_friends_button.click()
        time.sleep(5)
    except Exception as e:
        print(f" Could not navigate back to friends list after {target_name}: {e}")

print("\n All done!")
driver.quit()
