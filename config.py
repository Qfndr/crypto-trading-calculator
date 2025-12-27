import json
import os
from datetime import datetime

class Config:
    def __init__(self):
        self.config_file = 'config.json'
        self.data = self.load_config()
        
        # Default values
        self.capital = self.data.get('capital', 1000)
        self.risk_percent = self.data.get('risk_percent', 1.0)
        self.fee_percent = self.data.get('fee_percent', 0.04)
        self.selected_exchange = self.data.get('selected_exchange', 'Binance')
        self.order_type = self.data.get('order_type', 'taker')
        self.theme = self.data.get('theme', 'light')
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self, capital, risk_percent, fee_percent, exchange, order_type, theme):
        self.capital = capital
        self.risk_percent = risk_percent
        self.fee_percent = fee_percent
        self.selected_exchange = exchange
        self.order_type = order_type
        self.theme = theme
        
        self.data.update({
            'capital': capital,
            'risk_percent': risk_percent,
            'fee_percent': fee_percent,
            'selected_exchange': exchange,
            'order_type': order_type,
            'theme': theme,
            'last_updated': datetime.now().isoformat()
        })
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        
        return True
