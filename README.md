# 📊 Crypto Trading Calculator

## v1.6.1 (Hotfix)

- Settings window now includes **API Key/Secret** section per exchange and persists them in `config.json`. [file:1]
- Font download is now **non-blocking** and uses multiple sources (GitHub raw + jsDelivr mirror) to reduce failures in some networks. [file:2][web:136]
- Dark mode and language switching remain instant and are saved in config. [file:2]

## Install

```bash
git clone https://github.com/Qfndr/crypto-trading-calculator.git
cd crypto-trading-calculator
pip install -r requirements.txt
python main.py
```

## Update (Important)

The Update button checks the `VERSION` from remote `main.py` on GitHub and updates core files from the `main` branch (it does not require GitHub Releases). [file:2]
