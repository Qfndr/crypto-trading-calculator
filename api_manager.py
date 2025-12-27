import requests
import json
import time
from datetime import datetime

class APIManager:
    def __init__(self):
        self.apis = {
            'Binance': {
                'base_url': 'https://api.binance.com',
                'ticker_endpoint': '/api/v3/ticker/price',
                'requires_key': False
            },
            'CoinEx': {
                'base_url': 'https://api.coinex.com',
                'ticker_endpoint': '/v1/market/ticker',
                'requires_key': False
            },
            'Bybit': {
                'base_url': 'https://api.bybit.com',
                'ticker_endpoint': '/v5/market/tickers',
                'requires_key': False
            }
        }
        self.cache = {}
        self.cache_duration = 10  # seconds
    
    def get_price(self, exchange, symbol='BTCUSDT'):
        """Get current price from exchange API"""
        try:
            # Check cache first
            cache_key = f"{exchange}_{symbol}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_duration:
                    return cached_data
            
            if exchange == 'Binance':
                price = self._get_binance_price(symbol)
            elif exchange == 'CoinEx':
                price = self._get_coinex_price(symbol)
            elif exchange == 'Bybit':
                price = self._get_bybit_price(symbol)
            else:
                return None
            
            # Cache the result
            if price:
                self.cache[cache_key] = (price, time.time())
            
            return price
        except Exception as e:
            print(f"Error getting price: {e}")
            return None
    
    def _get_binance_price(self, symbol):
        url = f"{self.apis['Binance']['base_url']}{self.apis['Binance']['ticker_endpoint']}"
        params = {'symbol': symbol}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        return None
    
    def _get_coinex_price(self, symbol):
        # CoinEx uses different symbol format (e.g., BTCUSDT)
        url = f"{self.apis['CoinEx']['base_url']}{self.apis['CoinEx']['ticker_endpoint']}"
        params = {'market': symbol}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return float(data['data']['ticker']['last'])
        return None
    
    def _get_bybit_price(self, symbol):
        url = f"{self.apis['Bybit']['base_url']}{self.apis['Bybit']['ticker_endpoint']}"
        params = {'category': 'spot', 'symbol': symbol}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                return float(data['result']['list'][0]['lastPrice'])
        return None
    
    def get_available_symbols(self, exchange='Binance'):
        """Get list of available trading pairs"""
        common_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
            'DOGEUSDT', 'SOLUSDT', 'MATICUSDT', 'DOTUSDT', 'LTCUSDT',
            'AVAXUSDT', 'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT'
        ]
        return common_symbols
