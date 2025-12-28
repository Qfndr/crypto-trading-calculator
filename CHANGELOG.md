## [1.7.0] - 2025-12-28

### Changed
- **Professional Update System**: Migrated from raw file checks to **GitHub Releases**.
- App now checks `https://api.github.com/repos/Qfndr/crypto-trading-calculator/releases/latest`.
- Downloads `main.py` asset attached to the release instead of raw code.
- Version bump to 1.7.0 to signify architecture change.

### Fixed
- Enforced absolute paths in update scripts.
- Optimized imports and UI loading.
