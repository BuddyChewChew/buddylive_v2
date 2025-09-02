import gzip
import io
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Channel mapping from EPGShare01 IDs to display names
CHANNEL_MAPPING = {
    "A.and.E.US.-.Eastern.Feed.us": "A&E",
    "ACC.Network.us": "ACC Network",
    "AMC.-.Eastern.Feed.us": "AMC",
    "American.Heroes.Channel.us": "American Heroes Channel",
    "Animal.Planet.US.-.East.us": "Animal Planet",
    "BBC.America.-.East.us": "BBC America",
    "BBC.World.News.North.America.(BBCWN).us": "BBC World News HD",
    "BET.-.Eastern.Feed.us": "BET",
    "BET.Her.us": "BET Her",
    "Big.Ten.Network.us": "Big Ten Network",
    "Bloomberg.TV.USA.us": "Bloomberg TV",
    "Boomerang.us": "Boomerang",
    "Bravo.USA.-.Eastern.Feed.us": "Bravo",
    "Buzzr.TV.us": "Buzzr",
    "Cartoon.Network.USA.-.Eastern.Feed.us": "Cartoon Network",
    "CBS.Sports.Network.USA.us": "CBS Sports Network",
    "Cinemax.-.Eastern.Feed.us": "Cinemax",
    "CNBC.USA.us": "CNBC",
    "CMT.US.-.Eastern.Feed.us": "CMT",
    "CNN.us": "CNN",
    "Comedy.Central.(US).-.Eastern.Feed.us": "Comedy Central",
    "The.Cooking.Channel.us": "Cooking Channel",
    "C-SPAN.us": "C-SPAN",
    "C-SPAN.2.us": "CSPAN 2",
    "Destination.America.us": "Destination America",
    "Discovery.Channel.(US).-.Eastern.Feed.us": "Discovery",
    "Discovery.Family.Channel.us": "Discovery Family Channel",
    "Discovery.Life.Channel.us": "Discovery Life",
    "Disney.-.Eastern.Feed.us": "Disney Channel (East)",
    "Disney.Junior.USA.-.East.us": "Disney Junior",
    "Disney.XD.USA.-.Eastern.Feed.us": "Disney XD",
    "E!.Entertainment.USA.-.Eastern.Feed.us": "E!",
    "ESPN.us": "ESPN",
    "ESPN2.us": "ESPN2",
    "ESPN.News.us": "ESPNews",
    "ESPNU.On.Demand.us": "ESPNU",
    "Food.Network.USA.-.Eastern.Feed.us": "Food Network",
    "Fox.Business.us": "Fox Business Network",
    "Fox.News.us": "FOX News Channel",
    "Fox.Sports.1.us": "FOX Sports 1",
    "Fox.Sports.2.us": "FOX Sports 2",
    "Freeform.-.East.Feed.us": "Freeform",
    "FUSE.TV.-.Eastern.feed.us": "Fuse HD",
    "FX.Networks.East.Coast.us": "FX",
    "FX.Movie.Channel.us": "FX Movie",
    "FXX.USA.-.Eastern.us": "FXX",
    "FYI.USA.-.Eastern.us": "FYI",
    "Golf.Channel.USA.us": "Golf Channel",
    "Hallmark.-.Eastern.Feed.us": "Hallmark",
    "Hallmark.Drama.HDTV.(HALDRHD).us": "Hallmark Drama HD",
    "Hallmark.Mystery.Eastern.-.HD.us": "Hallmark Movies & Mysteries HD",
    "HBO.-.Eastern.Feed.us": "HBO East",
    "HBO.2.-.Eastern.Feed.us": "HBO 2 East",
    "HBO.Comedy.HD.-.East.us": "HBO Comedy HD",
    "HBO.Family.-.Eastern.Feed.us": "HBO Family East",
    "HBO.Signature.(HBO.3).-.Eastern.us": "HBO Signature",
    "HBO.Zone.HD.-.East.us": "HBO Zone HD",
    "HGTV.USA.-.Eastern.Feed.us": "HGTV",
    "History.Channel.US.-.Eastern.Feed.us": "History",
    "HLN.us": "HLN",
    "IFC.HDTV.(East).us": "IFC",
    "Investigation.Discovery.USA.-.Eastern.us": "Investigation Discovery",
    "ION..-.Eastern.Feed.us": "ION Television East HD",
    "Lifetime.Network.US.-.Eastern.Feed.us": "Lifetime",
    "Lifetime.Movies.-.East.us": "LMN",
    "LOGO.-.East.us": "Logo",
    "MeTV.Toons.us": "MeTV Toons",
    "MLB.Network.us": "MLB Network",
    "MoreMax..Eastern.us": "MoreMAX",
    "Motor.Trend.HD.us": "MotorTrend HD",
    "MSNBC.USA.us": "MSNBC",
    "MTV.USA.-.Eastern.Feed.us": "MTV",
    "National.Geographic.US.-.Eastern.us": "National Geographic",
    "National.Geographic.Wild.us": "Nat Geo WILD",
    "NBA.TV.USA.us": "NBA TV",
    "NewsMax.TV.us": "Newsmax TV",
    "NFL.Network.us": "NFL Network",
    "NFL.RedZone.us": "NFL Red Zone",
    "NHL.Network.USA.us": "NHL Network",
    "Nick.Jr..-.East.us": "Nick Jr.",
    "Nickelodeon.USA.-.East.Feed.us": "Nickelodeon East",
    "Nicktoons.-.East.us": "Nicktoons",
    "Outdoor.Channel.US.us": "Outdoor Channel",
    "Oprah.Winfrey.Network.USA.Eastern.us": "OWN",
    "True.Crime.TV.us": "Oxygen True Crime",
    "PBS.(WNET).New.York,.NY.us": "PBS 13 (WNET) New York",
    "ReelzChannel.us": "ReelzChannel",
    "Science.us": "Science",
    "SEC.Network.us": "SEC Network",
    "Showtime.2.-.Eastern.us": "Showtime (E)",
    "Showtime.Extreme.-.Eastern.us": "SHOWTIME 2",
    "Starz.-.Eastern.us": "STARZ East",
    "SundanceTV.USA.-.East.us": "SundanceTV HD",
    "Syfy.-.Eastern.Feed.us": "SYFY",
    "TBS.-.East.us": "TBS",
    "Turner.Classic.Movies.USA.us": "TCM",
    "TeenNick.-.Eastern.us": "TeenNick",
    "Telemundo..-.Eastern.Feed.us": "Telemundo East",
    "The.Tennis.Channel.us": "Tennis Channel",
    "WPIX.New.York.(SUPERSTATION).us": "The CW (WPIX New York)",
    "The.Movie.Channel.HDTV.(East).us": "The Movie Channel East",
    "The.Weather.Channel.us": "The Weather Channel",
    "TLC.USA.-.Eastern.us": "TLC",
    "TNT.-.Eastern.Feed.us": "TNT",
    "Travel.US.-.East.us": "Travel Channel",
    "truTV.USA.-.Eastern.us": "truTV",
    "TV.One.us": "TV One HD",
    "Universal.Kids.us": "Universal Kids",
    "Univision.-.Eastern.Feed.us": "Univision East",
    "USA.Network.-.East.Feed.us": "USA Network",
    "VH1.-.Eastern.Feed.us": "VH1",
    "VICE.us": "VICE",
    "WE.(Women&apos;s.Entertainment).-.Eastern.us": "WE tv",
    "ABC.(WABC).New.York,.NY.us": "WABC (New York) ABC East",
    "CBS.(WCBS).New.York,.NY.us": "WCBS (New York) CBS East",
    "NBC.(WNBC).New.York,.NY.us": "WNBC (New York) NBC East",
    "FOX.(WNYW).New.York,.NY.us": "WNYW (New York) FOX East"
}

class EPGShare01Fetcher:
    def __init__(self, cache_dir: str = "epg_cache"):
        """Initialize the EPG fetcher with optional cache directory."""
        self.sources = [
            "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz",
            "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS2.xml.gz"
        ]
        self.cache_dir = cache_dir
        self.epg_data = None
        self.last_fetch = None
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _download_with_retry(self, url: str, max_retries: int = 3) -> Optional[bytes]:
        """Download content with retry logic."""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                return response.content
            except (requests.RequestException, ConnectionError) as e:
                if attempt == max_retries - 1:
                    print(f"Failed to download {url} after {max_retries} attempts: {e}")
                    return None
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff

    def _download_epg(self) -> str:
        """Download and combine EPG data from all sources."""
        all_data = []
        
        for url in self.sources:
            print(f"Downloading from {url}...")
            content = self._download_with_retry(url)
            if content:
                try:
                    with gzip.GzipFile(fileobj=io.BytesIO(content)) as f:
                        all_data.append(f.read().decode('utf-8', errors='replace'))
                    print(f"Successfully downloaded from {url}")
                except Exception as e:
                    print(f"Error processing {url}: {e}")
        
        if not all_data:
            raise Exception("Failed to download EPG data from all sources")
        
        # Combine XML data
        combined = all_data[0]
        for data in all_data[1:]:
            # Remove XML declaration and root tags
            content = data[data.find('>')+1:]  # Remove XML declaration
            content = content[content.find('>')+1:]  # Remove opening root tag
            content = content[:content.rfind('</')]  # Remove closing root tag
            combined = combined.replace('</tv>', '') + content + '</tv>'
        
        return combined

    def get_epg_data(self, force_refresh: bool = False) -> str:
        """Get EPG data, using cached version if recent enough."""
        cache_file = os.path.join(self.cache_dir, "epg_cache.xml")
        now = datetime.now()
        
        # Check if we have a recent cache
        if not force_refresh and os.path.exists(cache_file):
            cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if (now - cache_time) < timedelta(hours=1):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # Fetch fresh data
        epg_data = self._download_epg()
        
        # Save to cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(epg_data)
            
        return epg_data

def generate_epg(channel_mapping: Dict[str, str], days: int = 3, output_file: str = "epg.xml") -> None:
    """
    Generate EPG XML for the specified channels and number of days.
    
    Args:
        channel_mapping: Dictionary mapping channel IDs to display names
        days: Number of days to include in the EPG (default: 3)
        output_file: Path to save the generated EPG file
    """
    fetcher = EPGShare01Fetcher()
    
    try:
        print("Fetching EPG data...")
        epg_data = fetcher.get_epg_data()
        root = ET.fromstring(epg_data)
        
        # Create a new XML tree for the output
        tv = ET.Element("tv")
        
        # Add channels to the output
        for channel_id, display_name in channel_mapping.items():
            channel_elem = ET.SubElement(tv, "channel", id=channel_id)
            ET.SubElement(channel_elem, "display-name").text = display_name
        
        # Process programs for each day
        for day in range(days):
            current_date = datetime.now() + timedelta(days=day)
            date_str = current_date.strftime('%Y%m%d')
            print(f"Processing programs for {current_date.date()}...")
            
            # Find all programs for our channels on this date
            for channel_id in channel_mapping.keys():
                programs = []
                
                # Find all programs for this channel
                for program in root.findall(f".//programme[@channel='{channel_id}']"):
                    start_time = program.get('start', '')
                    if not start_time.startswith(date_str):
                        continue
                        
                    # Create a copy of the program element
                    program_copy = ET.Element("programme")
                    program_copy.attrib.update(program.attrib)
                    
                    # Copy all child elements
                    for child in program:
                        program_copy.append(child)
                    
                    # Add to our programs list
                    tv.append(program_copy)
        
        # Pretty print the XML
        ET.indent(tv)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
            f.write(ET.tostring(tv, encoding='unicode'))
        
        print(f"EPG generated successfully: {output_file}")
        print(f"Channels included: {len(channel_mapping)}")
        
    except Exception as e:
        print(f"Error generating EPG: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate EPG from EPGShare01 sources')
    parser.add_argument('--days', type=int, default=3, help='Number of days to include in the EPG (default: 3)')
    parser.add_argument('--output', type=str, default='epg.xml', help='Output file path (default: epg.xml)')
    args = parser.parse_args()
    
    print("Starting EPG generation...")
    generate_epg(
        channel_mapping=CHANNEL_MAPPING,
        days=args.days,
        output_file=args.output
    )
