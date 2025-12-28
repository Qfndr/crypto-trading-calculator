## [1.6.6] - 2025-12-28

### Fixed
- Fixed app not starting (single Tk root + proper mainloop).
- Fixed updater running from System32 by enforcing script directory in apply_update.bat (cd /d %~dp0).
- Expanded language list to include fa,en,tr,ru,ar,hi,zh,ja,fr,it,bg (non-fa fall back to English strings).
- Added basic error logging to %USERPROFILE%\.crypto_calculator\app.log.
