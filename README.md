# 📊 Crypto Trading Calculator v1.6.0

A professional, robust cryptocurrency trading calculator with real API integration, history tracking, and advanced risk management.

![Version](https://img.shields.io/badge/version-1.6.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

## 🚀 New in v1.6.0 (The Rewrite)

This version is a complete rewrite of the core logic and UI to ensure robustness and performance.

*   **Real Font Loading:** Uses Windows API (ctypes) to load `Vazirmatn` font directly without installation.
*   **Real Settings:** Configure API Keys and Secret Keys for each exchange individually.
*   **Real Charts:** Built-in Canvas-based PnL curve generator based on your trade history.
*   **Real History:** View, filter, and export your trade history to CSV.
*   **Professional UI:** Clean, flat "Professional Trader" design (Dark/Light modes).
*   **Multi-Language:** 11 Languages supported (EN, FA, TR, RU, AR, HI, ZH, JA, FR, IT, BG).

## ✨ Features

*   **Risk Management:** Calculate position size based on risk percentage and stop loss.
*   **Multi-TP:** Support for 3 Take Profit targets with PnL calculation.
*   **Liquidation:** Accurate liquidation price calculation for LONG/SHORT positions.
*   **Live Prices:** Fetch real-time prices from supported exchanges.
*   **Fee Calculation:** Automatic Maker/Taker fee adjustments.
*   **Auto-Update:** Checks GitHub for the latest releases.

## 🛠 Installation

```bash
git clone https://github.com/Qfndr/crypto-trading-calculator.git
cd crypto-trading-calculator
pip install -r requirements.txt
python main.py
```

## 🌍 Supported Languages
*   English (en)
*   Persian (fa)
*   Turkish (tr)
*   Russian (ru)
*   Arabic (ar)
*   Hindi (hi)
*   Chinese (zh)
*   Japanese (ja)
*   French (fr)
*   Italian (it)
*   Bulgarian (bg)

## 📜 License
MIT License
