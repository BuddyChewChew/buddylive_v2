import requests
import gzip
import io
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from channel_mapping import channel_names

def fetch_epgshare01_data():
    """Fetch EPG data from EPGShare01 sources."""
    sources = [
        "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz"
    ]
    
    all_programs = {}
    
    for url in sources:
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Decompress the gzipped content
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
                
            # Parse the XML
            root = ET.fromstring(content)
            
            # Process each programme element
            for programme in root.findall('.//programme'):
                channel_id = programme.get('channel')
                if channel_id not in all_programs:
                    all_programs[channel_id] = []
                    
                # Extract program details
                program = {
                    'start': programme.get('start'),
                    'stop': programme.get('stop'),
                    'title': programme.findtext('title', '').strip(),
                    'desc': programme.findtext('desc', '').strip(),
                    'category': [cat.text for cat in programme.findall('category') if cat.text],
                    'icon': None
                }
                
                # Get icon if available
                icon = programme.find('icon')
                if icon is not None:
                    program['icon'] = icon.get('src')
                
                all_programs[channel_id].append(program)
                
        except Exception as e:
            print(f"Error fetching EPG data from {url}: {str(e)}")
    
    return all_programs

def prettify(elem, level=0):
    """Add indentation to the XML element."""
    indent = "\n" + level * "    "  # Four spaces for each level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for subelem in elem:
            prettify(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent

def create_xml(programs):
    """Create XMLTV formatted EPG data from program information."""
    root = ET.Element("tv")
    
    # Add channel information for each channel
    for channel_name, channel_programs in programs.items():
        # Get the EPGShare01 channel ID, defaulting to the channel name if not found
        channel_id = channel_names.get(channel_name, channel_name)
        
        # Special case for A&E channel
        if channel_name == "A&E":
            channel_id = "A.and.E.US.-.Eastern.Feed.us"
            
        # Create channel element
        channel_elem = ET.SubElement(root, "channel", {"id": channel_id})
        
        # Add display name
        display_name = ET.SubElement(channel_elem, "display-name")
        display_name.set("lang", "en")
        display_name.text = channel_name
        
        # Add icon if available
        if channel_id in channel_names.values():
            icon_elem = ET.SubElement(channel_elem, "icon")
            icon_elem.set("src", f"https://epgshare01.online/logos/{channel_id}.png")
    
    # Add programs
    for channel_name, programs in programs.items():
        # Get the EPGShare01 channel ID
        channel_id = channel_names.get(channel_name, channel_name)
        if channel_name == "A&E":
            channel_id = "A.and.E.US.-.Eastern.Feed.us"
            
        for program in programs:
            # Create program element
            program_elem = ET.SubElement(root, "programme", {
                "start": program.get('start', ''),
                "stop": program.get('stop', ''),
                "channel": channel_id
            })
            
            # Add title
            title_elem = ET.SubElement(program_elem, "title")
            title_elem.set("lang", "en")
            title_elem.text = program.get('title', 'Unknown')
            
            # Add description
            if program.get('desc'):
                desc_elem = ET.SubElement(program_elem, "desc")
                desc_elem.set("lang", "en")
                desc_elem.text = program['desc']
            
            # Add categories
            for category in program.get('category', []):
                if category:  # Only add non-empty categories
                    cat_elem = ET.SubElement(program_elem, "category")
                    cat_elem.set("lang", "en")
                    cat_elem.text = category
            
            # Add icon if available
            if program.get('icon'):
                icon_elem = ET.SubElement(program_elem, "icon")
                icon_elem.set("src", program['icon'])
    
    # Format the XML with proper indentation
    prettify(root)
    
    # Convert to string and return
    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode()

# Main execution
if __name__ == "__main__":
    # Fetch EPG data from EPGShare01
    print("Fetching EPG data from EPGShare01...")
    all_programs = fetch_epgshare01_data()

    if all_programs:
        print(f"Found data for {len(all_programs)} channels")
        
        # Map channel display names to their EPG data
        channel_programs = {}
        for epg_id, programs in all_programs.items():
            # Find the display name for this EPG ID
            display_name = None
            for name, id_val in channel_names.items():
                if id_val == epg_id:
                    display_name = name
                    break
            
            if display_name:
                channel_programs[display_name] = programs
        
        # Generate the XML
        print("Generating XML...")
        xml_output = create_xml(channel_programs)
        
        # Save to file
        output_file = "epg.xml"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_output)
        
        print(f"EPG XML generated successfully! Saved to {output_file}")
        print(f"Channels processed: {len(channel_programs)}")
    else:
        print("Failed to fetch EPG data")
