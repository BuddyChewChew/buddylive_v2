# py/videolivetv.py
import os
import random
import time
import json
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Add your user agents here
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.35 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
]

# Minimal channel logos mapping (extend as needed)
channel_logos = {
    "A&E": "https://cdn.tvpassport.com/image/station/960x540/v2/s10036_h15_aa.png",
    "ESPN": "https://cdn.tvpassport.com/image/station/240x135/v2/s10179_h15_aa.png",
    # Add other channels...
}

# Setup Chrome driver service
chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = webdriver.ChromeOptions()
# Headless recommended in CI
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--crash-dumps-dir=/tmp")
chrome_options.add_argument("--window-size=1920,1080")

# allow overriding binary location via CHROME_PATH env var (set in workflow)
chrome_binary = os.environ.get("CHROME_PATH", "/usr/bin/chromium-browser")
if chrome_binary:
    try:
        chrome_options.binary_location = chrome_binary
    except Exception:
        pass

# Random user agent
user_agent = random.choice(user_agents)
chrome_options.add_argument(f"user-agent={user_agent}")

# Initialize driver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

url = "https://thetvapp.to/"
driver.get(url)

wait = WebDriverWait(driver, 10)
try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "row")))
except Exception:
    # proceed even if page structure changes; links extraction may fail but we will handle gracefully
    pass

# Find the Live TV Channels row and links
live_tv_links = []
try:
    live_tv_row = driver.find_element(By.XPATH, "//h3[contains(text(), 'Live TV Channels')]/..")
    links = live_tv_row.find_elements(By.TAG_NAME, "a")
    for link in links:
        channel_name = link.text.strip()
        link_url = link.get_attribute("href")
        if channel_name and link_url:
            live_tv_links.append((channel_name, link_url))
except Exception:
    # fallback: try collecting all anchor links on page
    try:
        anchors = driver.find_elements(By.TAG_NAME, "a")
        for a in anchors:
            text = a.text.strip()
            href = a.get_attribute("href")
            if text and href and "thetvapp.to" in href:
                live_tv_links.append((text, href))
    except Exception:
        pass

# Print M3U header
print("#EXTM3U")

for name, link in live_tv_links:
    # default fallback values
    m3u8_urls = []
    m3u8_url = "https://github.com/BuddyChewChew/buddylive_v2/raw/refs/heads/main/en/offline.mp4"
    logo_url = channel_logos.get(name, "")

    try:
        driver.get(link)
        # allow page to load and network requests to fire
        time.sleep(4)

        # get performance entries (network requests)
        raw = driver.execute_script("return JSON.stringify(performance.getEntries());")
        network_requests = []
        if raw:
            try:
                network_requests = json.loads(raw)
            except Exception:
                network_requests = []

        # filter .m3u8 urls
        m3u8_urls = [entry.get("name") for entry in network_requests if entry.get("name") and ".m3u8" in entry.get("name")]

        # clean urls that embed a real url in a query param like mu=
        cleaned = []
        for u in m3u8_urls:
            if "ping.gif" in u and "mu=" in u:
                try:
                    parsed = urllib.parse.urlparse(u)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if "mu" in qs:
                        decoded = urllib.parse.unquote(qs["mu"][0])
                        cleaned.append(decoded)
                    else:
                        cleaned.append(u)
                except Exception:
                    cleaned.append(u)
            else:
                cleaned.append(u)

        if cleaned:
            m3u8_url = cleaned[0]
    except Exception as e:
        # log and continue with fallback
        print(f"# error extracting for {name}: {e}", flush=True)

    # Always print an entry for the channel
    print(f"#EXTINF:-1 group-title=\"USA TV\" tvg-ID=\"{name}\" tvg-name=\"{name}\" tvg-logo=\"{logo_url}\", {name}")
    print(m3u8_url)

driver.quit()
