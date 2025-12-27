# Changelog

All notable changes to Crypto Trading Calculator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-12-28

### 🎉 Major Features Added

#### 🌍 Multi-Language Support
- **Complete Persian/English Translation System**
  - All UI elements translated
  - Language switcher button in top bar
  - Automatic language persistence
  - Modular translation system (`language.py`)
  - 100+ translation keys

#### 🎨 Modern Apple-Inspired Design
- **Glassmorphism-Inspired UI**
  - Clean, minimal design
  - Subtle shadows and borders
  - Rounded corners throughout
  - Modern color gradients
  - Improved spacing and padding
  - Professional card layouts

#### 🔄 Auto-Update System from GitHub
- **Complete Update Manager**
  - Check for updates button in toolbar
  - Automatic version comparison
  - Direct download from GitHub
  - Version selector (install any version)
  - Automatic file backup before update
  - One-click update to latest
  - Restart application after update
  - Update history and changelog display

#### 📊 200+ Trading Symbols Added
- **Comprehensive Symbol List**
  - All major cryptocurrencies
  - TON, SOL, DOGE, SHIB, PEPE
  - DeFi tokens (AAVE, UNI, CAKE, etc.)
  - Layer 1 & 2 (ARB, OP, MATIC, etc.)
  - Meme coins (FLOKI, BONK, WIF, etc.)
  - AI tokens (FET, AGIX, RENDER, etc.)
  - Gaming & Metaverse (SAND, MANA, AXS, etc.)
  - NFT related tokens
  - Exchange tokens
  - Privacy coins
  - And much more!

### ✨ Enhancements
- Improved UI responsiveness
- Better error handling
- Enhanced API integration
- Optimized performance

### 📝 Files Added
- `language.py` - Translation system
- `updater.py` - Update manager
- `VERSION` - Version tracking
- `CHANGELOG.md` - This file

---

## [1.3.0] - 2025-12-28

### ✨ Features

#### 🌙 Complete Dark Mode Fix
- **All UI Elements Now Properly Themed**
  - Fixed white background in dark mode
  - Entry fields with correct colors
  - Labels with proper contrast
  - Canvas and scrollbar theming
  - Text widgets with dark background
  - All borders and highlights themed

#### 🔤 IranSans Font Integration
- **Professional Persian Typography**
  - IranSans font for all Persian text
  - Automatic fallback to Tahoma if unavailable
  - Better text rendering
  - Improved readability
  - Multiple font weights (normal, bold)
  - Consistent font sizing

#### ⚙️ Complete Settings Panel
- **API Keys for All Exchanges**
  - Binance API Key & Secret
  - CoinEx API Key & Secret
  - Bybit API Key & Secret
  - OKX API Key & Secret
  - KuCoin API Key & Secret
  - Gate.io API Key & Secret
  - Bitget API Key & Secret
  - MEXC API Key & Secret
  - Secure storage in config.json
  - Password-masked secret keys
  - Scrollable settings window

#### 🔧 Enhanced Configuration
- Price refresh rate setting
- Persistent API key storage
- Settings backup system
- Better config management

### 🐛 Bug Fixes
- Fixed dark mode white elements
- Fixed Entry field colors in dark mode
- Fixed Label backgrounds
- Fixed text visibility issues
- Fixed theme persistence

### 📝 Files Modified
- `main.py` - Complete UI overhaul
- `config.py` - API keys support

---

## [1.2.0] - 2025-12-27

### ✨ Features

#### 📈 Charts & Analysis
- **P&L Chart**
  - Visual profit/loss representation
  - Entry, SL, and TP markers
  - Profit and loss zones
  - Theme-aware colors
  - Professional matplotlib integration

- **Trade History Analysis**
  - Bar chart of past trades
  - Cumulative profit display
  - Win/loss visualization
  - Historical performance tracking

#### 📡 Live Price API Integration
- **Multi-Exchange Support**
  - Binance API
  - CoinEx API  
  - Bybit API
  - Live price fetching
  - 10-second smart caching
  - Auto-fill entry price
  - Network error handling

#### 🎨 Modern UI Redesign
- **Card-Based Layout**
  - Modern card design for each section
  - Improved visual hierarchy
  - Better spacing and padding
  - Emoji icons for sections
  - Cleaner organization

#### 🌙 Dark Mode (Initial)
- Dark/Light theme toggle
- Theme persistence
- Partial implementation (improved in v1.3.0)

#### ⚙️ Settings Panel
- Advanced settings window
- API key storage (Binance only in this version)
- Refresh rate configuration

### 📝 Files Added
- `api_manager.py` - API integration
- `chart_generator.py` - Chart creation
- `requirements.txt` - Dependencies

### 🐛 Known Issues
- Dark mode incomplete (fixed in v1.3.0)
- Limited API key support (fixed in v1.3.0)

---

## [1.1.0] - 2025-12-26

### ✨ Features

#### 📊 Enhanced Calculations
- **Risk Management**
  - Position size calculation
  - Risk/Reward ratio for each TP
  - Liquidation price calculation
  - Fee calculations (entry + exit)
  - Percentage-based metrics

- **Multiple Take Profits**
  - Support for 3 TPs
  - Individual R/R for each TP
  - Visual indicators (✅/⚠️/❌)
  - Profit calculation per TP

#### 🏦 Exchange Presets
- **12 Exchange Support**
  - Binance, CoinEx, Bybit
  - OKX, KuCoin, Gate.io
  - Bitget, MEXC
  - Nobitex, Wallex, Exir
  - Custom/Manual
  - Automatic fee setting
  - Maker/Taker selection

#### 💾 Data Persistence
- **Trade History**
  - JSON-based storage
  - Automatic save after calculation
  - Trade metadata tracking
  - CSV export functionality

- **Configuration**
  - Settings persistence
  - Last used values
  - Exchange memory

### 📝 Files Added
- `config.py` - Configuration management
- `trade_history.py` - History tracking

---

## [1.0.0] - 2025-12-25

### ✨ Initial Release

#### 📊 Core Features
- **Basic Calculator**
  - Entry price input
  - Stop loss calculation
  - Take profit calculation
  - Long/Short position support
  - Leverage support (1-100x)

- **Capital Management**
  - Total capital input
  - Risk percentage
  - Position size calculation
  - Fee calculation

#### 📝 Results Display
- Position size in USDT
- Coin quantity
- Entry and exit fees
- Potential profit/loss
- Formatted output

#### 🎨 UI
- Basic Tkinter interface
- Persian text support
- Simple form layout
- Calculate button
- Results text area

### 📝 Files
- `main.py` - Main application
- `README.md` - Basic documentation

---

## Version Comparison

| Feature | v1.0.0 | v1.1.0 | v1.2.0 | v1.3.0 | v1.4.0 |
|---------|--------|--------|--------|--------|--------|
| Basic Calculator | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multiple TPs | ❌ | ✅ | ✅ | ✅ | ✅ |
| Exchange Presets | ❌ | ✅ | ✅ | ✅ | ✅ |
| History | ❌ | ✅ | ✅ | ✅ | ✅ |
| Live Price API | ❌ | ❌ | ✅ | ✅ | ✅ |
| Charts | ❌ | ❌ | ✅ | ✅ | ✅ |
| Dark Mode | ❌ | ❌ | ⚠️ | ✅ | ✅ |
| IranSans Font | ❌ | ❌ | ❌ | ✅ | ✅ |
| All API Keys | ❌ | ❌ | ❌ | ✅ | ✅ |
| Multi-Language | ❌ | ❌ | ❌ | ❌ | ✅ |
| Auto-Update | ❌ | ❌ | ❌ | ❌ | ✅ |
| 200+ Symbols | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Roadmap

### 🔜 Upcoming Features

#### v1.5.0 (Planned)
- [ ] TradingView chart integration
- [ ] Technical indicators
- [ ] Real-time price alerts
- [ ] Portfolio tracking
- [ ] Multi-position calculator

#### v1.6.0 (Planned)
- [ ] Automated trading signals
- [ ] Copy trading suggestions
- [ ] Risk analytics dashboard
- [ ] Backtesting system

#### v2.0.0 (Future)
- [ ] Web version
- [ ] Mobile app (iOS/Android)
- [ ] Cloud sync
- [ ] Social features
- [ ] Premium features

---

## Contributors

- **Qfndr** - Original Author & Maintainer
- Thanks to all users for feedback and suggestions!

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/Qfndr/crypto-trading-calculator/issues)
- 💡 Feature requests: [GitHub Issues](https://github.com/Qfndr/crypto-trading-calculator/issues)
- ⭐ Star the project if you like it!

## License

MIT License - See LICENSE file for details
