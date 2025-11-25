from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import random
import time
import json
import urllib.parse

user_agents = [
    #add your list of user agents here
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.35 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (X11; Linux i686; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/127.0 Mobile/15E148 Safari/605.1.15',
    'Mozilla/5.0 (Android 14; Mobile; rv:127.0) Gecko/126.0 Firefox/126.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',

]


# Dictionary mapping channel IDs to channel names
channel_logos = {
    "WABC (New York) ABC East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/1-abc-blue-us.png?raw=true",
    "WCBS (New York) CBS East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/1-cbs-logo-white-us.png?raw=true",
    "WNBC (New York) NBC East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/1-nbc.png?raw=true",
    "WNYW (New York) FOX East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/1-FOX-blue.png?raw=true",
    "A&E": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/a-and-e-us.png?raw=true",
    "ACC Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/acc-network-us.png?raw=true",
    "AMC": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/amc-us.png?raw=true",
    "American Heroes Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/american-heroes-channel-us.png?raw=true",
    "Animal Planet": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/animal-planet-us.png?raw=true",
    "BBC America": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/bbc-america-us.png?raw=true",
    "BBC World News HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/bbc-news-uk.png?raw=true",
    "BET": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/bet-us.png?raw=true",
    "BET Her": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/bet-her-us.png?raw=true",
    "Big Ten Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/big-ten-network-us.png?raw=true",
    "Bloomberg TV": "https://cdn.tvpassport.com/image/station/240x135/v2/s71799_h15_ab.png",
    "Boomerang": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/boomerang-us.png?raw=true",
    "Bravo": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/bravo-us.png?raw=true",
    "Cartoon Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cartoon-network-us.png?raw=true",
    "CBS Sports Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cbs-sports-us.png?raw=true",
    "Cinemax": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cinemax-us.png?raw=true",
    "CNBC": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cnbc-us.png?raw=true",
    "CMT": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cmt-color-us.png?raw=true",
    "CNN": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cnn-us.png?raw=true",
    "Comedy Central": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/comedy-central-us.png?raw=true",
    "Cooking Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cooking-channel-us.png?raw=true",
    "Crime & Investigation HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/crime-and-investigation-us.png?raw=true",
    "CSPAN": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/c-span-1-us.png?raw=true",
    "CSPAN 2": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/c-span-2-us.png?raw=true",
    "Destination America": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/destination-america-us.png?raw=true",
    "Discovery": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/discovery-channel-icon-us.png?raw=true",
    "Discovery Family Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/discovery-family-us.png?raw=true",
    "Discovery Life": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/discovery-life-us.png?raw=true",
    "Disney Channel (East)": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/disney-channel-us.png?raw=true",
    "Disney Junior": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/disney-jr-us.png?raw=true",
    "Disney XD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/disney-xd-us.png?raw=true",
    "E!": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/e-entertainment-us.png?raw=true",
    "ESPN": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/espn-us.png?raw=true",
    "ESPN2": "https://cdn.tvpassport.com/image/station/240x135/v2/s12444_h15_ab.png",
    "ESPNews": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/espnews-us.png?raw=true",
    "ESPNU": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/espn-us.png?raw=true",
    "Food Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/food-network-us.png?raw=true",
    "Fox Business Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fox-business-us.png?raw=true",
    "FOX News Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fox-news-us.png?raw=true",
    "FOX Sports 1": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fox-sports-1-us.png?raw=true",
    "FOX Sports 2": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fox-sports-2-us.png?raw=true",
    "Freeform": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/freeform-us.png?raw=true",
    "Fuse HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fuse-us.png?raw=true",
    "FX": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fx-us.png?raw=true",
    "FX Movie": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fxm-movie-channel-us.png?raw=true",
    "FXX": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fxx-us.png?raw=true",
    "FYI": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/fyi-us.png?raw=true",
    "Golf Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/golf-channel-ar.png?raw=true",
    "Hallmark": "https://github.com/tv-logo/tv-logos/blob/main/countries/united-states/hallmark-tv-us.png?raw=true",
    "Hallmark Drama HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hallmark-channel-us.png?raw=true",
    "Hallmark Movies & Mysteries HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hallmark-mystery-us.png?raw=true",
    "HBO East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo.png?raw=true",
    "HBO 2 East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo-2.png?raw=true",
    "HBO Comedy HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo-comedy.png?raw=true",
    "HBO Family East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo-family-us.png?raw=true",
    "HBO Signature": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo-sig.png?raw=true",
    "HBO Zone HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hbo-zone.png?raw=true",
    "HGTV": "https://github.com/tv-logo/tv-logos/blob/main/countries/united-states/hgtv-us.png?raw=true",
    "History": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/history-channel-us.png?raw=true",
    "HLN": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/hln-us.png?raw=true",
    "IFC": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/ifc-us.png?raw=true",
    "Investigation Discovery": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/investigation-discovery-us.png?raw=true",
    "ION Television East HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/ion-television-us.png?raw=true",
    "Lifetime": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/lifetime-us.png?raw=true",
    "LMN": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/lifetime-movie-network-us.png?raw=true",
    "Logo": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/logo-us.png?raw=true",
    "MeTV Toons":"https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/me-tv-toons-us.png?raw=true",
    "MLB Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/mlb-network-us.png?raw=true",
    "MoreMAX": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cinemax-us.png?raw=true",
    "MotorTrend HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/motor-trend-us.png?raw=true",
    "MovieMAX": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/cinemax-us.png?raw=true",
    "MSNBC": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/msnbc-alt-us.png?raw=true",
    "MTV": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/mtv-us.png?raw=true",
    "Nat Geo WILD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nat-geo-wild-us.png?raw=true",
    "National Geographic": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/national-geographic-us.png?raw=true",
    "NBA TV": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nba-tv-icon-us.png?raw=true",
    "Newsmax TV": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/newsmax-tv-us.png?raw=true",
    "NFL Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nfl-icon-us.png?raw=true",
    "NFL Red Zone": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nfl-red-zone-us.png?raw=true",
    "NHL Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nhl-network-us.png?raw=true",
    "Nick Jr.": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nick-jr-us.png?raw=true",
    "Nickelodeon East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nickelodeon-us.png?raw=true",
    "Nicktoons": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/nick-toons-us.png?raw=true",
    "Outdoor Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/outdoor-channel-us.png?raw=true",
    "OWN": "https://cdn.tvpassport.com/image/station/240x135/v2/s70387_h15_aa.png",
    "Oxygen True Crime": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/oprah-winfrey-network-us.png?raw=true",
    "PBS 13 (WNET) New York": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/pbs-us.png?raw=true",
    "ReelzChannel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/reelz-us.png?raw=true",
    "Science": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/discovery-science-icon-us.png?raw=true",
    "SEC Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/sec-network-us.png?raw=true",
    "Showtime (E)": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/showtime-icon-us.png?raw=true",
    "SHOWTIME 2": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/showtime2-icon-us.png?raw=true",
    "STARZ East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/starz-us.png?raw=true",
    "SundanceTV HD": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/sundance-tv-us.png?raw=true",
    "SYFY": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/syfy-us.png?raw=true",
    "TBS": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tbs-us.png?raw=true",
    "TCM": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tcm-us.png?raw=true",
    "TeenNick": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/teen-nick-us.png?raw=true",
    "Telemundo East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/telemundo-us.png?raw=true",
    "Tennis Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tennis-channel-us.png?raw=true",
    "The CW (WPIX New York)": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/the-cw-us.png?raw=true",
    "The Movie Channel East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/the-movie-channel-icon-us.png?raw=true",
    "The Weather Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/weather-channel-us.png?raw=true",
    "TLC": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tlc-us.png?raw=true",
    "TNT": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tnt-us.png?raw=true",
    "Travel Channel": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/travel-channel-us.png?raw=true",
    "truTV": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/tru-tv-us.png?raw=true",
    "TV One HD": "https://github.com/tv-logo/tv-logos/blob/main/countries/united-states/one-tv-us.png?raw=true",
    "Universal Kids": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/universal-kids-us.png?raw=true",
    "Univision East": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/univision-us.png?raw=true",
    "USA Network": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/usa-us.png?raw=true",
    "VH1": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/vh1-us.png?raw=true",
    "VICE": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/vice-us.png?raw=true",
    "WE tv": "https://github.com/BuddyChewChew/buddylive_v2/blob/main/logos/we-tv-us.png?raw=true"

    # Add more channel IDs and names as needed
}

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())


# Set Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--crash-dumps-dir=/tmp")

# Randomly select a user agent
user_agent = random.choice(user_agents)
chrome_options.add_argument(f"user-agent={user_agent}")

# Initialize the Chrome WebDriver with the specified options
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

# Open the webpage
url = "https://thetvapp.to/"
driver.get(url)


# Wait for the page to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "row")))

# Find the Live TV Channels row
live_tv_row = driver.find_element(By.XPATH, "//h3[contains(text(), 'Live TV Channels')]/..")

# Find all links in the Live TV Channels row
links = live_tv_row.find_elements(By.TAG_NAME, "a")

# Initialize a list to store the links
live_tv_links = []

# Iterate over each link
for link in links:
    # Get the channel name
    channel_name = link.text.strip()
    
    # Get the link URL and add it to the list
    link_url = link.get_attribute("href")
    live_tv_links.append((channel_name, link_url))

# Print the M3U header
print("#EXTM3U")

# Iterate over each live TV channel link
for name, link in live_tv_links:
    # Navigate to the link URL
    driver.get(link)

    try:
        # Wait for the button to be clickable
        wait = WebDriverWait(driver, 5)
        #try:
            # Try to find loadVideoBtnOne first
        #    video_button = wait.until(EC.element_to_be_clickable((By.ID, 'loadVideoBtn')))
        #except:
            # If loadVideoBtnOne is not found, look for loadVideoBtnTwo
        #    video_button = wait.until(EC.element_to_be_clickable((By.ID, 'loadVideoBtnTwo')))
        #video_button.click()

        # Wait for a brief period to allow the page to load and network requests to be made
        time.sleep(5)

        # Get all network requests
        network_requests = driver.execute_script("return JSON.stringify(performance.getEntries());")

        # Convert the string back to a list of dictionaries in Python
        network_requests = json.loads(network_requests)

        # Get the logo URL for the current channel
        logo_url = channel_logos.get(name)


        # Filter out only the URLs containing ".m3u8"
        m3u8_urls = [request["name"] for request in network_requests if ".m3u8" in request["name"]]

        cleaned_m3u8_urls = []

        for url in m3u8_urls:
            if "ping.gif" in url and "mu=" in url:
                try:
                    parsed = urllib.parse.urlparse(url)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    if "mu" in query_params:
                        real_url = urllib.parse.unquote(query_params["mu"][0])
                        cleaned_m3u8_urls.append(real_url)
                    else:
                        # If "mu" not found, just keep the original
                        cleaned_m3u8_urls.append(url)
                except Exception as e:
                    print(f"Error decoding URL: {url} -> {e}")
                    cleaned_m3u8_urls.append(url)
            else:
                # Not ping.gif, just keep the original
                cleaned_m3u8_urls.append(url)

        # Use the cleaned list (which includes all original URLs if they didn't need cleaning)
        m3u8_urls = cleaned_m3u8_urls

        # Print the collected m3u8 URLs
        if m3u8_urls:
            m3u8_url = m3u8_urls[0]
        else:
            m3u8_url = "https://github.com/mikekaprielian/rtnaodhor93n398/raw/main/en/offline.mp4"
    except Exception as e:
        # If an exception occurs (e.g., button not found), use the default link
        m3u8_url = "https://github.com/mikekaprielian/rtnaodhor93n398/raw/main/en/offline.mp4"

    # Print the collected m3u8 URL
    if m3u8_urls:
        print(f"#EXTINF:-1 group-title=\"USA TV\" tvg-ID=\"{name}\" tvg-name=\"{name}\" tvg-logo=\"{logo_url}\", {name}")
        print(m3u8_url)  # Print only the first m3u8 URL


# Close the WebDriver
driver.quit()



