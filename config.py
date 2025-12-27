import json
import os

class Config:
    def __init__(self):
        self.config_file = 'config.json'
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.capital = data.get('capital', 100)
                    self.risk_percent = data.get('risk_percent', 1)
                    self.fee_percent = data.get('fee_percent', 0.04)
                    self.selected_exchange = data.get('exchange', 'Binance')
                    self.order_type = data.get('order_type', 'taker')
                    self.theme = data.get('theme', 'light')
            except:
                self.set_defaults()
        else:
            self.set_defaults()
    
    def set_defaults(self):
        self.capital = 100
        self.risk_percent = 1
        self.fee_percent = 0.04
        self.selected_exchange = 'Binance'
        self.order_type = 'taker'
        self.theme = 'light'
    
    def save_config(self, capital, risk_percent, fee_percent, exchange, order_type, theme):
        data = {
            'capital': capital,
            'risk_percent': risk_percent,
            'fee_percent': fee_percent,
            'exchange': exchange,
            'order_type': order_type,
            'theme': theme
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
