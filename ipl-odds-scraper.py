from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd 
import numpy as np

# ✅ Set your path to the ChromeDriver you placed on Desktop
CHROMEDRIVER_PATH = "/Users/gauthamvecham/Desktop/chrome-for-web-scraping/chromedriver-mac-arm64/chromedriver"

# Start the Chrome browser using Selenium
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))

# List of URLs to scrape
urls = [
    "https://www.oddsportal.com/cricket/india/ipl/results/#/page/1/",
    "https://www.oddsportal.com/cricket/india/ipl/results/#/page/2/"
]

match_data = []  # this will store [team1, team2, odd1, odd2] for each match

for url in urls:
    driver.get(url)
    print(f"Waiting for page to load: {url}")
    time.sleep(20)

    # Handle cookie consent (only on the first page load)
    if url == urls[0]:
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_button.click()
            print("Accepted cookies")
            time.sleep(2)
        except Exception as e:
            print("Could not handle cookie consent:", e)

    print("Looking for event blocks...")
    event_blocks = driver.find_elements(By.CSS_SELECTOR, 'div[data-v-c685125c][class*="eventRow"]')
    print(f"Found {len(event_blocks)} event blocks on {url}")

    for block in event_blocks:
        try:
            teams = block.find_elements(By.CSS_SELECTOR, 'p[class*="participant-name"]')
            odds = block.find_elements(By.CSS_SELECTOR, 'p[data-testid^="odd-container"]')
            print(f"Found {len(teams)} teams and {len(odds)} odds in this block")
            if len(teams) == 2 and len(odds) >= 2:
                team1 = teams[0].text.strip()
                team2 = teams[1].text.strip()
                odd1 = odds[0].text.strip()
                odd2 = odds[1].text.strip()
                match_data.append([team1, team2, odd1, odd2])
                print(f"Added match: {team1} vs {team2}")
        except Exception as e:
            print("Skipping a match due to:", e)

driver.quit()

print("\nFinal match data:")
print(match_data)

print(len(match_data))

# Save match_data to CSV in row format: Team 1, Team 2, Odds 1, Odds 2
df = pd.DataFrame(match_data, columns=["Team 1", "Team 2", "Odds 1", "Odds 2"])
df.to_csv("ipl_odds_list.csv", index=False)
print("\nSaved match list to ipl_odds_list.csv") 