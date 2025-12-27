import requests
import json
import os
import sys
import subprocess
from pathlib import Path

class Updater:
    def __init__(self):
        self.github_repo = "Qfndr/crypto-trading-calculator"
        self.api_base = f"https://api.github.com/repos/{self.github_repo}"
        self.raw_base = f"https://raw.githubusercontent.com/{self.github_repo}"
        self.current_version = self.get_current_version()
    
    def get_current_version(self):
        """Get current version from VERSION file"""
        try:
            if os.path.exists('VERSION'):
                with open('VERSION', 'r') as f:
                    return f.read().strip()
            return "1.4.0"
        except:
            return "1.4.0"
    
    def get_latest_version(self):
        """Get latest version from GitHub"""
        try:
            response = requests.get(f"{self.api_base}/releases/latest", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('tag_name', '').replace('v', '')
            return None
        except:
            return None
    
    def get_all_versions(self):
        """Get all available versions from GitHub"""
        try:
            response = requests.get(f"{self.api_base}/releases", timeout=10)
            if response.status_code == 200:
                releases = response.json()
                versions = []
                for release in releases:
                    tag = release.get('tag_name', '').replace('v', '')
                    if tag:
                        versions.append({
                            'version': tag,
                            'name': release.get('name', tag),
                            'published': release.get('published_at', ''),
                            'body': release.get('body', '')
                        })
                return versions
            return []
        except:
            return []
    
    def get_file_from_github(self, filepath, version='main'):
        """Download file from GitHub"""
        try:
            url = f"{self.raw_base}/{version}/{filepath}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
            return None
        except:
            return None
    
    def download_version(self, version='main'):
        """Download and install specific version"""
        files_to_update = [
            'main.py',
            'config.py',
            'trade_history.py',
            'api_manager.py',
            'chart_generator.py',
            'language.py',
            'updater.py',
            'VERSION',
            'requirements.txt',
            'README.md'
        ]
        
        updated_files = []
        failed_files = []
        
        for filepath in files_to_update:
            try:
                content = self.get_file_from_github(filepath, version)
                if content:
                    # Backup original file
                    if os.path.exists(filepath):
                        backup_path = f"{filepath}.backup"
                        with open(filepath, 'r', encoding='utf-8') as f:
                            backup_content = f.read()
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(backup_content)
                    
                    # Write new file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    updated_files.append(filepath)
                else:
                    failed_files.append(filepath)
            except Exception as e:
                failed_files.append(f"{filepath} ({str(e)})")
        
        return {
            'success': len(failed_files) == 0,
            'updated': updated_files,
            'failed': failed_files
        }
    
    def check_for_update(self):
        """Check if update is available"""
        latest = self.get_latest_version()
        if latest and latest != self.current_version:
            return {
                'available': True,
                'current': self.current_version,
                'latest': latest
            }
        return {
            'available': False,
            'current': self.current_version,
            'latest': latest or self.current_version
        }
    
    def update_to_latest(self):
        """Update to latest version"""
        return self.download_version('main')
    
    def update_to_version(self, version):
        """Update to specific version"""
        return self.download_version(f"v{version}")
    
    def restart_app(self):
        """Restart the application"""
        try:
            python = sys.executable
            script = sys.argv[0]
            subprocess.Popen([python, script])
            sys.exit(0)
        except:
            pass
