from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Set path to the ChromeDriver
CHROMEDRIVER_PATH = "/Users/gauthamvecham/Desktop/chrome-for-web-scraping/chromedriver-mac-arm64/chromedriver"

# Initialize the Chrome browser
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))

# This list will hold all match data as [team1, team2, odd1, odd2]
match_data = []

# Function to extract match information from the current page
def extract_matches():
    # Find all match containers on the page
    event_blocks = driver.find_elements(By.CSS_SELECTOR, 'div[data-v-c685125c][class*="eventRow"]')
    print(f"Found {len(event_blocks)} event blocks")

    # Loop through each match block and extract data
    for block in event_blocks:
        try:
            teams = block.find_elements(By.CSS_SELECTOR, 'p[class*="participant-name"]')
            odds = block.find_elements(By.CSS_SELECTOR, 'p[data-testid^="odd-container"]')

            if len(teams) == 2 and len(odds) >= 2:
                team1 = teams[0].text.strip()
                team2 = teams[1].text.strip()
                odd1 = odds[0].text.strip()
                odd2 = odds[1].text.strip()
                match_data.append([team1, team2, odd1, odd2])
                print(f"Added: {team1} vs {team2} → {odd1}, {odd2}")
        except Exception as e:
            print("Skipping a match due to an error:", e)

# Load Page 1
driver.get("https://www.oddsportal.com/cricket/india/ipl/results/#/page/1/")
print("Loaded Page 1")
time.sleep(8)  # Wait for content to load

# Handle cookie popup if present
try:
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    )
    cookie_button.click()
    print("Accepted cookie popup")
except Exception:
    print("No cookie popup found or already handled")

# Extract matches from Page 1
extract_matches()

# Try to click the "2" button to go to Page 2
try:
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@data-number="2"]'))
    )
    next_button.click()
    print("Clicked Page 2")
    time.sleep(8)  # Wait for content to load
    extract_matches()  # Extract matches from Page 2
except Exception as e:
    print("Could not load Page 2:", e)

# Close the browser
driver.quit()

# Convert match data into a DataFrame and save as CSV
df = pd.DataFrame(match_data, columns=["Team 1", "Team 2", "Odds 1", "Odds 2"])
df.to_csv("ipl_odds_list.csv", index=False)
print(f"Saved {len(match_data)} matches to ipl_odds_list-2.csv")