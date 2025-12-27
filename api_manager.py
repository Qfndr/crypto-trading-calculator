"""
API Manager for Crypto Trading Calculator
Handles connections to multiple exchanges
"""

import requests
from datetime import datetime

class APIManager:
    def __init__(self):
        self.exchanges = {
            'Binance': 'https://api.binance.com/api/v3/ticker/price?symbol=',
            'Bybit': 'https://api.bybit.com/v2/public/tickers?symbol=',
            'OKX': 'https://www.okx.com/api/v5/market/ticker?instId=',
            'KuCoin': 'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=',
            'Gate.io': 'https://api.gateio.ws/api/v4/spot/tickers?currency_pair=',
            'Bitget': 'https://api.bitget.com/api/spot/v1/market/ticker?symbol=',
            'MEXC': 'https://api.mexc.com/api/v3/ticker/price?symbol=',
            'CoinEx': 'https://api.coinex.com/v1/market/ticker?market=',
        }
        
        # 200+ Most popular trading symbols
        self.symbols = [
            # Top 20 by Market Cap
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
            'LINKUSDT', 'TRXUSDT', 'TONUSDT', 'UNIUSDT', 'ATOMUSDT',
            'LTCUSDT', 'ETCUSDT', 'NEARUSDT', 'APTUSDT', 'FILUSDT',
            
            # DeFi Tokens
            'AAVEUSDT', 'MKRUSDT', 'COMPUSDT', 'SNXUSDT', 'CRVUSDT',
            'SUSHIUSDT', '1INCHUSDT', 'YFIUSDT', 'BALUSDT', 'UMAUMA',
            'BANDUSDT', 'LRCUSDT', 'KSMUSDT', 'CAKEUSDT', 'LUNAUSDT',
            
            # Layer 1 Blockchains
            'ARBUSDT', 'OPUSDT', 'SUIUSDT', 'APTUSDT', 'SEIUSDT',
            'INJUSDT', 'TIAUSDT', 'CFXUSDT', 'FTMUSDT', 'HBARUSDT',
            'ALGOUSDT', 'EGLDUSDT', 'ICPUSDT', 'FLOWUSDT', 'VETUSDT',
            
            # Layer 2 Solutions
            'ARBUSDT', 'OPUSDT', 'MATICUSDT', 'IMXUSDT', 'LDOUSDT',
            'METISUSDT', 'BELUSDT', 'STXUSDT', 'ZILUSDT', 'QNTUSDT',
            
            # Meme Coins
            'SHIBUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'BONKUSDT', 'WIFUSDT',
            'DOGENUSDT', 'SATSUSDT', 'RATSUSDT', 'MEMEUSDT', 'NEIRO',
            'TRUMPUSDT', 'MYROUSH', 'BOMEUSDT', 'MEWUSDT', 'MOGUSD',
            
            # Gaming & Metaverse
            'AXSUSDT', 'SANDUSDT', 'MANAUSDT', 'ENJUSDT', 'GALAUSDT',
            'IMXUSDT', 'GMTUSDT', 'APEUSD T', 'BLZUSDT', 'ALICEUSDT',
            'TLMUSDT', 'YGGUSDT', 'SLPUSDT', 'PAXGUSDT', 'RONINUSDT',
            'PIXELUSDT', 'BEAMU SDT', 'WAXPUSDT', 'ILVUSDT', 'XETAUSDT',
            
            # AI & Big Data
            'AGIXUSDT', 'FETUSDT', 'OCEANUSDT', 'RNDRTU SDT', 'GRTUSDT',
            'NMRUSDT', 'RLCUSDT', 'IQUSDT', 'AIUSDT', 'PHBUSDT',
            'CTXCUSDT', 'VITEUSDT', 'COTIUSDT', 'ATAUSH', 'NKNUS DT',
            
            # NFT Tokens
            'BLURUSH', 'LOOKSUSDT', 'X2Y2USDT', 'SUPERUSDT', 'RAREUSDT',
            'THETAUSDT', 'CHZUSDT', 'NFTUSDT', 'AUCTIONUSDT', 'DEWUSDT',
            
            # Exchange Tokens
            'BNBUSDT', 'CROUS DT', 'FTTUSDT', 'OKBUSDT', 'HTUSDT',
            'KCSUSDT', 'GTUSDT', 'MXUSDT', 'BTTUSDT', 'WBETHUSDT',
            
            # Stablecoins & Wrapped
            'USDCUSDT', 'BUSDUSDT', 'TUSDUSDT', 'DAIUSDT', 'USDPUSDT',
            'WBTCUSDT', 'WETHUSDT', 'STETHUSDT', 'FRAXUSDT', 'USTCUSDT',
            
            # Oracle & Data
            'LINKUSDT', 'BANDUSDT', 'TRBUS DT', 'DIAUSDT', 'APIUSDT',
            
            # Privacy Coins
            'XMRUSDT', 'ZECUSDT', 'DASHUSDT', 'SCRTUSDT', 'XVGUSDT',
            
            # Storage & Infrastructure
            'FILUSDT', 'ARUSDT', 'STORJUSDT', 'IOTXUSDT', 'BTTUSDT',
            'SCUSDT', 'ANKRUSDT', 'CKBUSDT', 'BLZUSDT', 'CELRUS DT',
            
            # Real World Assets
            'ONDOUSDT', 'RIOUSH', 'TRUSDT', 'GOLDUSDT', 'PAXGUSDT',
            
            # Social & Content
            'STEEMUSDT', 'HIVEUSD T', 'MASKUSDT', 'RALLYUSDT', 'CHZUSDT',
            
            # New Trending (2024-2025)
            'JUPUSDT', 'WUSDT', 'PYTHUSDT', 'DYMUSH', 'ALTUSDT',
            'TIAUSDT', 'XAIUSDT', 'ACEUSDT', 'NFPUSDT', 'AIUSDT',
            'PORTALUSDT', 'PDAUSDT', 'BOMEUSDT', 'ETHFIUSDT', 'ENAUSDT',
            
            # Additional Popular
            'CELOUSDT', 'WAVESUSDT', 'ONTUSDT', 'RVNUSDT', 'KAVAUSDT',
            'ZILUSDT', 'ICXUSDT', 'IOSTUSDT', 'OMGUSDT', 'OGNUSDT',
            'LSKUSDT', 'ZENUSDT', 'QTUMUS DT', 'BATUSDT', 'REPUSDT',
        ]
        
    def get_available_symbols(self):
        """Return list of available trading symbols"""
        return sorted(self.symbols)
    
    def get_price(self, exchange, symbol):
        """
        Get current price for symbol from specified exchange
        Returns: float price or None if error
        """
        try:
            if exchange not in self.exchanges:
                return None
            
            url = self.exchanges[exchange] + symbol
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse based on exchange
                if exchange == 'Binance':
                    return float(data['price'])
                elif exchange == 'Bybit':
                    if 'result' in data:
                        return float(data['result'][0]['last_price'])
                elif exchange == 'OKX':
                    if 'data' in data and len(data['data']) > 0:
                        return float(data['data'][0]['last'])
                elif exchange == 'KuCoin':
                    if 'data' in data:
                        return float(data['data']['price'])
                elif exchange == 'Gate.io':
                    if len(data) > 0:
                        return float(data[0]['last'])
                elif exchange == 'Bitget':
                    if 'data' in data:
                        return float(data['data']['close'])
                elif exchange == 'MEXC':
                    return float(data['price'])
                elif exchange == 'CoinEx':
                    if 'data' in data and 'ticker' in data['data']:
                        return float(data['data']['ticker']['last'])
        except Exception as e:
            print(f"Error fetching price from {exchange}: {e}")
            return None
        
        return None
    
    def get_24h_stats(self, exchange, symbol):
        """
        Get 24h statistics (high, low, volume, change)
        Returns: dict with stats or None
        """
        try:
            if exchange == 'Binance':
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'high': float(data['highPrice']),
                        'low': float(data['lowPrice']),
                        'volume': float(data['volume']),
                        'change': float(data['priceChangePercent'])
                    }
        except Exception as e:
            print(f"Error fetching 24h stats: {e}")
            return None
        
        return None
