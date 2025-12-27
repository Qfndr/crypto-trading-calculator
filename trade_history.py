import json
import os
from datetime import datetime

class TradeHistory:
    def __init__(self):
        self.history_file = 'trade_history.json'
        self.trades = self.load_history()
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def add_trade(self, trade_data):
        trade_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.trades.append(trade_data)
        self.save_history()
    
    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=4)
    
    def get_trades(self, limit=None):
        if limit:
            return self.trades[-limit:]
        return self.trades
    
    def clear_history(self):
        self.trades = []
        self.save_history()
    
    def export_to_csv(self, filename='trades_export.csv'):
        import csv
        if not self.trades:
            return False
        
        keys = self.trades[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.trades)
        return True
