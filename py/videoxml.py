"""
TV Channels EPG Generator
This script generates a simple XMLTV EPG file for TV channels.
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz

# TV Channel Configuration
CHANNELS = {
    # News
    "cnn": {"name": "CNN", "logo": "https://logo.clearbit.com/cnn.com"},
    "bbc-news": {"name": "BBC News", "logo": "https://logo.clearbit.com/bbc.com"},
    "fox-news": {"name": "Fox News", "logo": "https://logo.clearbit.com/foxnews.com"},
    
    # Entertainment
    "hbo": {"name": "HBO", "logo": "https://logo.clearbit.com/hbo.com"},
    "netflix": {"name": "Netflix", "logo": "https://logo.clearbit.com/netflix.com"},
    "disney": {"name": "Disney Channel", "logo": "https://logo.clearbit.com/disney.com"},
    
    # Sports
    "espn": {"name": "ESPN", "logo": "https://logo.clearbit.com/espn.com"},
    "nfl": {"name": "NFL Network", "logo": "https://logo.clearbit.com/nfl.com"},
    
    # Movies
    "hbo-movies": {"name": "HBO Movies", "logo": "https://logo.clearbit.com/hbomax.com"},
    "tcm": {"name": "Turner Classic Movies", "logo": "https://logo.clearbit.com/tcm.com"},
    
    # Kids
    "cartoon-network": {"name": "Cartoon Network", "logo": "https://logo.clearbit.com/cartoonnetwork.com"},
    "nickelodeon": {"name": "Nickelodeon", "logo": "https://logo.clearbit.com/nick.com"},
}

# Timezone configuration
TZ = pytz.timezone('America/New_York')

def create_epg():
    """Create the EPG XML structure."""
    root = ET.Element("tv", {
        "generator-info-name": "TV Channels EPG",
        "generator-info-url": "https://github.com/yourusername/buddylive"
    })
    
    # Add channels
    for channel_id, channel_info in CHANNELS.items():
        channel = ET.SubElement(root, "channel", id=channel_id)
        ET.SubElement(channel, "display-name").text = channel_info["name"]
        if channel_info.get("logo"):
            ET.SubElement(channel, "icon", {"src": channel_info["logo"]})
    
    # Add some sample programs (you can replace this with real program data)
    now = datetime.now(TZ)
    for channel_id in CHANNELS.keys():
        for hour in range(24):  # 24 hours of programming
            start_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            program = ET.SubElement(root, "programme", {
                "start": start_time.strftime("%Y%m%d%H%M%S %z"),
                "stop": end_time.strftime("%Y%m%d%H%M%S %z"),
                "channel": channel_id
            })
            
            ET.SubElement(program, "title").text = f"Sample Program {hour+1}"
            ET.SubElement(program, "desc").text = f"Description for sample program {hour+1}"
            ET.SubElement(program, "category").text = "Entertainment"
    
    # Format the XML with proper indentation
    from xml.dom import minidom
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return "\n".join([line for line in xml_str.split("\n") if line.strip()])

if __name__ == "__main__":
    print(create_epg())
