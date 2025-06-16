
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Path to ChromeDriver
CHROMEDRIVER_PATH = "/Users/gauthamvecham/Desktop/chrome-for-web-scraping/chromedriver-mac-arm64/chromedriver"
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))

match_data = []

def scroll_page():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def extract_matches(year):
    scroll_page()
    event_blocks = driver.find_elements(By.CSS_SELECTOR, 'div[data-v-c685125c][class*="eventRow"]')
    print(f"\nFound {len(event_blocks)} matches for {year}")
    count = 0
    for block in event_blocks:
        try:
            teams = block.find_elements(By.CSS_SELECTOR, 'p[class*="participant-name"]')
            odds = block.find_elements(By.CSS_SELECTOR, 'p[data-testid^="odd-container"]')
            if len(teams) == 2 and len(odds) >= 2:
                team1 = teams[0].text.strip()
                team2 = teams[1].text.strip()
                odd1 = odds[0].text.strip()
                odd2 = odds[1].text.strip()
                match_data.append([team1, team2, odd1, odd2, year])
                print(f"{team1} vs {team2} → {odd1}, {odd2} ({year})")
                count += 1
        except Exception as e:
            print("Skipping match due to error:", e)
    return count

# ============ IPL 2025 ============
driver.get("https://www.oddsportal.com/cricket/india/ipl/results/")
time.sleep(8)

# Handle cookie popup once
try:
    cookie_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_btn.click()
    time.sleep(2)
except Exception:
    print("No cookie popup or already accepted")

# Page 1 - 2025
matches_2025_p1 = extract_matches(2025)

# Page 2 - 2025
try:
    page_2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@data-number="2"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", page_2)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", page_2)
    time.sleep(8)
    matches_2025_p2 = extract_matches(2025)
except Exception as e:
    print("Page 2 (2025) click failed:", e)
    matches_2025_p2 = 0

# ============ IPL 2024 ============
driver.get("https://www.oddsportal.com/cricket/india/ipl-2024/results/")
time.sleep(8)

# Page 1 - 2024
matches_2024_p1 = extract_matches(2024)

# Page 2 - 2024
try:
    page_2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@data-number="2"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", page_2)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", page_2)
    time.sleep(8)
    matches_2024_p2 = extract_matches(2024)
except Exception as e:
    print("Page 2 (2024) click failed:", e)
    matches_2024_p2 = 0

# Close browser
driver.quit()

# Convert to DataFrame
df = pd.DataFrame(match_data, columns=["Team 1", "Team 2", "Odds 1", "Odds 2", "Year"])
df.to_csv("ipl_odds_full.csv", index=False)

# === Summary ===
total_2025 = matches_2025_p1 + matches_2025_p2
total_2024 = matches_2024_p1 + matches_2024_p2
print(f"\n Saved {len(match_data)} matches to ipl_odds_full.csv")
print(f"Matches from 2025: {total_2025}")
print(f"Matches from 2024: {total_2024}")
print(f"Total matches scraped: {len(match_data)}")