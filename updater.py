"""
Auto-update system for Crypto Trading Calculator
Fetches latest version from GitHub and updates files
"""

import requests
import json
import os
from packaging import version

VERSION = "1.5.0"
REPO_OWNER = "Qfndr"
REPO_NAME = "crypto-trading-calculator"
GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

class Updater:
    def __init__(self):
        self.current_version = VERSION
        self.github_api = GITHUB_API
    
    def check_for_update(self):
        """
        Check if newer version exists on GitHub
        Returns: dict with 'available', 'latest', 'current'
        """
        try:
            # Get latest release
            response = requests.get(f"{self.github_api}/releases/latest", timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest = data['tag_name'].replace('v', '')
                
                available = version.parse(latest) > version.parse(self.current_version)
                
                return {
                    'available': available,
                    'latest': latest,
                    'current': self.current_version,
                    'url': data['html_url'],
                    'body': data.get('body', '')
                }
            else:
                # If no releases, check tags
                response = requests.get(f"{self.github_api}/tags", timeout=10)
                if response.status_code == 200 and response.json():
                    tags = response.json()
                    latest = tags[0]['name'].replace('v', '')
                    available = version.parse(latest) > version.parse(self.current_version)
                    return {
                        'available': available,
                        'latest': latest,
                        'current': self.current_version,
                        'url': f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases",
                        'body': ''
                    }
        except Exception as e:
            print(f"Error checking for updates: {e}")
        
        return {
            'available': False,
            'latest': self.current_version,
            'current': self.current_version,
            'url': '',
            'body': ''
        }
    
    def get_all_versions(self):
        """
        Get list of all available versions from GitHub
        Returns: list of dicts with version info
        """
        versions = []
        try:
            # Try to get releases first
            response = requests.get(f"{self.github_api}/releases", timeout=10)
            if response.status_code == 200 and response.json():
                for release in response.json():
                    versions.append({
                        'version': release['tag_name'].replace('v', ''),
                        'name': release['name'],
                        'date': release['published_at'][:10],
                        'body': release.get('body', '')[:200]
                    })
            
            # If no releases, get tags
            if not versions:
                response = requests.get(f"{self.github_api}/tags", timeout=10)
                if response.status_code == 200:
                    for tag in response.json()[:20]:  # Limit to 20 tags
                        versions.append({
                            'version': tag['name'].replace('v', ''),
                            'name': tag['name'],
                            'date': 'N/A',
                            'body': 'No description'
                        })
        except Exception as e:
            print(f"Error fetching versions: {e}")
        
        return versions
    
    def update_to_latest(self):
        """
        Update to latest version from GitHub
        Downloads and replaces main Python files
        """
        try:
            update_info = self.check_for_update()
            if not update_info['available']:
                return {'success': False, 'message': 'Already up to date'}
            
            return self.update_to_version(update_info['latest'])
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_to_version(self, target_version):
        """
        Update to specific version
        Downloads files from GitHub repository
        """
        files_to_update = [
            'main.py',
            'config.py',
            'trade_history.py',
            'api_manager.py',
            'chart_generator.py',
            'language.py',
            'updater.py'
        ]
        
        updated = []
        failed = []
        
        try:
            for filename in files_to_update:
                try:
                    # Get file content from GitHub
                    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{filename}"
                    response = requests.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        # Backup original
                        if os.path.exists(filename):
                            backup_name = f"{filename}.backup"
                            with open(filename, 'r', encoding='utf-8') as f:
                                content = f.read()
                            with open(backup_name, 'w', encoding='utf-8') as f:
                                f.write(content)
                        
                        # Write new version
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        updated.append(filename)
                    else:
                        failed.append(filename)
                except Exception as e:
                    print(f"Error updating {filename}: {e}")
                    failed.append(filename)
            
            if updated:
                return {
                    'success': True,
                    'updated': updated,
                    'failed': failed,
                    'message': f"Updated {len(updated)} files successfully"
                }
            else:
                return {
                    'success': False,
                    'updated': [],
                    'failed': failed,
                    'message': 'No files were updated'
                }
        except Exception as e:
            return {
                'success': False,
                'updated': updated,
                'failed': failed,
                'message': str(e)
            }
