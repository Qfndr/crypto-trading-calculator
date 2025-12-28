"""
Auto-update system for Crypto Trading Calculator

Important:
- This updater does NOT depend on GitHub Releases/Tags.
- It compares local VERSION with VERSION found in remote main.py on GitHub.
- When updating, it downloads the latest files from the main branch.
"""

import os
import re
import requests
from packaging import version

REPO_OWNER = "Qfndr"
REPO_NAME = "crypto-trading-calculator"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main"

class Updater:
    def __init__(self, current_version: str):
        self.current_version = current_version

    def _get_remote_version(self):
        """Fetch remote main.py and extract VERSION = 'x.y.z' """
        url = f"{RAW_BASE}/main.py"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise RuntimeError(f"Could not fetch remote main.py (HTTP {r.status_code})")

        m = re.search(r"^VERSION\s*=\s*\"([^\"]+)\"", r.text, flags=re.MULTILINE)
        if not m:
            raise RuntimeError("Could not parse VERSION from remote main.py")
        return m.group(1)

    def check_for_update(self):
        try:
            latest = self._get_remote_version()
            available = version.parse(latest) > version.parse(self.current_version)
            return {
                'available': available,
                'latest': latest,
                'current': self.current_version,
                'url': f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
            }
        except Exception as e:
            return {
                'available': False,
                'latest': self.current_version,
                'current': self.current_version,
                'url': '',
                'error': str(e)
            }

    def update_to_latest(self):
        """Update core python files from main branch."""
        files_to_update = [
            'main.py',
            'config.py',
            'trade_history.py',
            'api_manager.py',
            'chart_generator.py',
            'language.py',
            'updater.py'
        ]

        updated, failed = [], []
        for filename in files_to_update:
            try:
                url = f"{RAW_BASE}/{filename}"
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    failed.append(filename)
                    continue

                # Backup
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                        old = f.read()
                    with open(f"{filename}.backup", 'w', encoding='utf-8') as f:
                        f.write(old)

                # Write new
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(r.text)

                updated.append(filename)
            except Exception:
                failed.append(filename)

        if updated:
            return {'success': True, 'updated': updated, 'failed': failed, 'message': f"Updated {len(updated)} files"}
        return {'success': False, 'updated': [], 'failed': failed, 'message': 'No files updated'}
