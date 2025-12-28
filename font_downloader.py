"""
Automatic Vazirmatn Font Downloader
Downloads the beautiful Vazirmatn font if not available
"""

import os
import requests
from pathlib import Path

FONT_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf"
FONT_PATH = "Vazirmatn-Regular.ttf"

def download_font():
    """
    Download Vazirmatn font if it doesn't exist
    """
    if os.path.exists(FONT_PATH):
        print(f"✅ Font already exists: {FONT_PATH}")
        return True
    
    try:
        print("📥 Downloading Vazirmatn font...")
        response = requests.get(FONT_URL, timeout=30)
        
        if response.status_code == 200:
            with open(FONT_PATH, 'wb') as f:
                f.write(response.content)
            print(f"✅ Font downloaded successfully: {FONT_PATH}")
            return True
        else:
            print(f"❌ Failed to download font. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error downloading font: {e}")
        return False

if __name__ == "__main__":
    download_font()
