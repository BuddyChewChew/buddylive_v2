name: Update VideoEvents and VideoLive

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  schedule:
    # Runs at 4:15 AM, 10:15 AM, 4:15 PM, 10:15 PM UTC (adjust if needed)
    - cron: '15 4,10,16,22 * * *'
  workflow_dispatch:

# Prevent race conditions: only one run at a time
concurrency:
  group: update-m3u-playlists
  cancel-in-progress: true

jobs:
  generate_m3u:
    runs-on: ubuntu-22.04
    permissions:
      contents: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Important for rebase

      - name: Create en Folder
        run: mkdir -p en

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install necessary packages
        run: |
          sudo apt-get update    
          sudo apt-get install -y unzip wget libnss3 libgconf-2-4 libxcb-xinerama0
          wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
          sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
          rm google-chrome-stable_current_amd64.deb

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 pandas webdriver-manager selenium selenium_stealth pytz

      - name: Run Python Script videoevents
        run: |
          python_output=$(python py/videoevents.py)
          echo "$python_output" > en/videoevents.m3u
          echo "$python_output" > en/videoall.m3u

      - name: Run Python Script videolivetv
        run: |
          python py/videolivetv.py | sed '/#EXTM3U/d' >> en/videoall.m3u

      - name: Extract Token and Update ESPN Links
        run: |
          # Extract the token from the last occurrence in videoall.m3u
          token=$(grep -oP '(?<=token=)[^"&]*' en/videoall.m3u | tail -1)
          
          if [ -z "$token" ]; then
            echo "Warning: No token found. Skipping ESPN link update."
          else
            echo "Found token: $token"
            sed -i "/tvg-name=\"ESPN\"/{n;s|https://[^[:space:]]*|https://v6.thetvapp.to/hls/ESPN/index.m3u8?token=$token|g}" en/videoall.m3u
            sed -i "/tvg-name=\"ESPN2\"/{n;s|https://[^[:space:]]*|https://v6.thetvapp.to/hls/ESPN2/index.m3u8?token=$token|g}" en/videoall.m3u
          fi

      - name: Pull latest changes to avoid conflicts
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git pull origin main --rebase || echo "Rebase failed, continuing..."

      - name: Commit and Push Changes
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Update M3U playlists and ESPN token"
          branch: main
          file_pattern: en/*.m3u
          repository: .
          push_options: '--force-with-lease'
          skip_dirty_check: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
