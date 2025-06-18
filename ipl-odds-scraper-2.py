from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

CHROMEDRIVER_PATH = "/Users/gauthamvecham/Desktop/chrome-for-web-scraping/chromedriver-mac-arm64/chromedriver"
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))

match_data = []

def scroll_to_top():
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def extract_matches(year):
    scroll_to_bottom()
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

# Start from the latest year
driver.get("https://www.oddsportal.com/cricket/india/ipl/results/")
time.sleep(8)

# Accept cookie popup once
try:
    cookie_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_btn.click()
    time.sleep(2)
except Exception:
    print("No cookie popup or already accepted")

# Loop from 2025 to 2010
for year in range(2025, 2009, -1):
    url = f"https://www.oddsportal.com/cricket/india/ipl-{year}/results/" if year != 2025 else "https://www.oddsportal.com/cricket/india/ipl/results/"
    print(f"\nLoading {year} data from {url}")
    driver.get(url)
    time.sleep(8)

    # Scroll from top to bottom on Page 1
    scroll_to_top()
    matches_p1 = extract_matches(year)

    # Try for Page 2
    try:
        page_2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@data-number="2"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", page_2)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", page_2)
        time.sleep(8)

        # Scroll to top and then bottom for Page 2
        scroll_to_top()
        matches_p2 = extract_matches(year)
    except Exception as e:
        print(f"Page 2 ({year}) click failed:", e)
        matches_p2 = 0

    print(f"Year {year}: {matches_p1 + matches_p2} matches scraped")

# Finalize and save
driver.quit()

df = pd.DataFrame(match_data, columns=["Team 1", "Team 2", "Odds 1", "Odds 2", "Year"])
df.to_csv("data/odds_2010_to_2025.csv", index=False)

print(f"\nSaved {len(match_data)} matches to odds_2010_to_2025.csv")