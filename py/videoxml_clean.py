import requests
import gzip
import io
import xml.etree.ElementTree as ET
from channel_mapping import channel_names

def fetch_epgshare01_data():
    """Fetch EPG data using iterparse to save memory."""
    sources = [
        "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz",
        "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz"
    ]
    
    # Create a reverse mapping: ID -> Name for faster lookup
    id_to_name = {v: k for k, v in channel_names.items()}
    # Manual override for A&E
    id_to_name["A.and.E.US.-.Eastern.Feed.us"] = "A&E"
    
    all_programs = {}
    target_ids = set(channel_names.values())
    target_ids.add("A.and.E.US.-.Eastern.Feed.us")

    for url in sources:
        print(f"📥 Downloading: {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Decompress in memory
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                # Use iterparse to handle large XML files without crashing RAM
                context = ET.iterparse(f, events=('end',))
                for event, elem in context:
                    if elem.tag == 'programme':
                        channel_id = elem.get('channel')
                        
                        # Only process programs for channels in our mapping
                        if channel_id in target_ids:
                            display_name = id_to_name.get(channel_id)
                            if display_name not in all_programs:
                                all_programs[display_name] = []
                            
                            program = {
                                'start': elem.get('start'),
                                'stop': elem.get('stop'),
                                'title': elem.findtext('title', '').strip(),
                                'desc': elem.findtext('desc', '').strip(),
                                'category': [cat.text for cat in elem.findall('category') if cat.text],
                                'icon': elem.find('icon').get('src') if elem.find('icon') is not None else None
                            }
                            all_programs[display_name].append(program)
                    
                    # Clear element to free memory
                    elem.clear()
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
    
    return all_programs

def create_xml(programs_by_name):
    """Generate the final filtered XMLTV file."""
    root = ET.Element("tv")
    
    # 1. Add Channel Headers
    for display_name, epg_id in channel_names.items():
        chan_elem = ET.SubElement(root, "channel", {"id": epg_id})
        dn = ET.SubElement(chan_elem, "display-name", {"lang": "en"})
        dn.text = display_name
        icon = ET.SubElement(chan_elem, "icon", {"src": f"https://epgshare01.online/logos/{epg_id}.png"})

    # 2. Add Programme Data
    for display_name, progs in programs_by_name.items():
        channel_id = channel_names.get(display_name, display_name)
        # Handle special A&E case
        if display_name == "A&E": channel_id = "A.and.E.US.-.Eastern.Feed.us"
            
        for p in progs:
            prog_elem = ET.SubElement(root, "programme", {
                "start": p['start'], "stop": p['stop'], "channel": channel_id
            })
            ET.SubElement(prog_elem, "title", {"lang": "en"}).text = p['title']
            if p['desc']:
                ET.SubElement(prog_elem, "desc", {"lang": "en"}).text = p['desc']
            for cat in p['category']:
                ET.SubElement(prog_elem, "category", {"lang": "en"}).text = cat
            if p['icon']:
                ET.SubElement(prog_elem, "icon", {"src": p['icon']})

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode()

if __name__ == "__main__":
    data = fetch_epgshare01_data()
    if data:
        output = create_xml(data)
        with open("epg.xml", "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ EPG generated for {len(data)} channels.")
