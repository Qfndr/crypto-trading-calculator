"""
Automatic font downloader for Crypto Trading Calculator
Downloads Vazirmatn font from GitHub releases
"""

import requests
import os
import zipfile
import shutil

def download_vazirmatn_font():
    """
    Download Vazirmatn font from official GitHub repository
    """
    font_file = "Vazirmatn-Regular.ttf"
    
    # Check if font already exists
    if os.path.exists(font_file):
        print(f"✅ Font already exists: {font_file}")
        return True
    
    try:
        print("📥 Downloading Vazirmatn font...")
        
        # Direct download URL for Vazirmatn font
        font_url = "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-font-v33.003.zip"
        
        # Download the zip file
        response = requests.get(font_url, timeout=30)
        
        if response.status_code == 200:
            zip_path = "vazirmatn_temp.zip"
            
            # Save zip file
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print("📦 Extracting font...")
            
            # Extract the zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the Regular TTF file
                for file in zip_ref.namelist():
                    if 'Vazirmatn-Regular.ttf' in file:
                        # Extract to current directory
                        source = zip_ref.open(file)
                        target = open(font_file, 'wb')
                        with source, target:
                            shutil.copyfileobj(source, target)
                        print(f"✅ Font installed: {font_file}")
                        break
            
            # Cleanup
            os.remove(zip_path)
            return True
        else:
            print(f"❌ Failed to download font: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading font: {e}")
        print("⚠️  App will use fallback font (Tahoma)")
        return False

if __name__ == "__main__":
    download_vazirmatn_font()
