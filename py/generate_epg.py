import os
import sys
from datetime import datetime, timedelta
import pytz
from videoxml import channel_names, channel_ids, scrape_tv_programming, create_xml

def generate_epg():
    # Create en directory if it doesn't exist
    os.makedirs('en', exist_ok=True)
    
    # Calculate dates for the next 3 days
    dates = [(datetime.now(pytz.UTC) + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]
    
    all_programs = {}
    
    # Scrape programming for each channel and date
    for channel_id in channel_ids:
        program_data = []
        for date in dates:
            try:
                program_data_for_date = scrape_tv_programming(channel_id, date)
                if program_data_for_date:
                    program_data.extend(program_data_for_date)
            except Exception as e:
                print(f"Error scraping {channel_id} for {date}: {str(e)}", file=sys.stderr)
                continue

        if program_data:
            all_programs[channel_id] = program_data
    
    # Create XML content
    xml_content = create_xml(all_programs)
    
    # Write to file
    with open('en/epg.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print("EPG XML generated successfully at en/epg.xml")

if __name__ == "__main__":
    generate_epg()
