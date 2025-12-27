import requests
import time
from datetime import datetime

class APIManager:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 10  # seconds
        
        # Comprehensive symbol list (200+ popular coins)
        self.symbols = [
            # Top Market Cap
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'TRXUSDT', 'TONUSDT', 'LINKUSDT',
            'MATICUSDT', 'DOTUSDT', 'LTCUSDT', 'SHIBUSDT', 'AVAXUSDT',
            'UNIUSDT', 'ATOMUSDT', 'XLMUSDT', 'ETCUSDT', 'FILUSDT',
            
            # DeFi Tokens
            'AAVEUSDT', 'MKRUSDT', 'COMPUSDT', 'SNXUSDT', 'CRVUSDT',
            'SUSHIUSDT', '1INCHUSDT', 'YFIUSDT', 'RENUSDT', 'BALUSDT',
            'BANDUSDT', 'CAKEUSDT', 'ALPACAUSDT', 'ALPINEUSDT',
            
            # Layer 1 & Layer 2
            'NEARUSDT', 'APTUSDT', 'SUIUSDT', 'ARBUSDT', 'OPUSDT',
            'FTMUSDT', 'ALGOUSDT', 'ICPUSDT', 'EOSUSDT', 'HBARUSDT',
            'VETUSDT', 'THETAUSDT', 'FLOWUSDT', 'EGLDUSDT', 'XTZUSDT',
            'ZILUSDT', 'IOTAUSDT', 'QNTUSDT', 'KAVAUSDT', 'RUNEUSDT',
            
            # Meme Coins
            'PEPEUSDT', 'FLOKIUSDT', 'BONKUSDT', 'WIF', 'MEMEUSDT',
            'BOMEUSDT', 'SATSUSDT', 'RATSUSDT', 'PEOPLEUSDT', 'LADYSUSDT',
            'BABYDOGEUSDT', 'KISHUUSDT', 'ELON', 'DOGELON',
            
            # AI & Big Data
            'FETUSDT', 'AGIXUSDT', 'OCEANUSDT', 'RNDR', 'GRTUSDT',
            'INJUSDT', 'THETAUSDT', 'IQUSDT', 'PHBUSDT', 'AITOKENUSDT',
            
            # Gaming & Metaverse
            'SANDUSDT', 'MANAUSDT', 'AXSUSDT', 'ENJUSDT', 'GALAUSDT',
            'CHZUSDT', 'THETAUSDT', 'GMTUSDT', 'APECOINUSDT', 'IMXUSDT',
            'BLZUSDT', 'MAGICUSDT', 'MCUSDT', 'MOVRUSDT', 'ILVSDT',
            
            # NFT Related
            'BLZUSDT', 'THETAUSDT', 'FLOWUSDT', 'RAREBLOCKSUSDT',
            
            # Exchange Tokens
            'BNBUSDT', 'FTMUSDT', 'CROUS', 'OKBUSDT', 'HTUSDT',
            'KCSUSDT', 'BTRUSDT', 'VRAUSDT', 'NEXOUSDT', 'LUNCUSDT',
            
            # Stablecoins & Wrapped
            'USDCUSDT', 'BUSDUSDT', 'TUSDUSDT', 'USDPUSDT', 'PAXGUSDT',
            'WBTCUSDT', 'WETHUSDT', 'RENBTCUSDT',
            
            # Privacy Coins
            'XMRUSDT', 'ZECUSDT', 'DASHUSDT', 'SCRTUSDT', 'BEAMUSDT',
            
            # Infrastructure
            'RENDERUSDT', 'ARUSDT', 'STORJUSDT', 'KSMUSDT', 'LDOUSDT',
            'GLMRUSDT', 'BATUSDT', 'ANTUSDT', 'CKBUSDT', 'CELRUSDT',
            
            # New & Trending
            'JUPUSDT', 'PYTHUSDT', 'TIAUSDT', 'DYMUSDT', 'PORTALUSDT',
            'PIXELUSDT', 'STRKUSDT', 'ACEUSDT', 'NFPUSDT', 'AIUSDT',
            'XAIUSDT', 'MANTAUSDT', 'ALTUSDT', 'WLDUSDT', 'EDUUSDT',
            
            # Top 100 Extended
            'BCHUSDT', 'NEOUSDT', 'LUNAUSDT', 'WAVESUSDT', 'ONTUSDT',
            'OMGUSDT', 'ZILUSDT', 'ICXUSDT', 'IOSTUSDT', 'ZRXUSDT',
            'LRCUSDT', 'QTUMUSDT', 'BATUSDT', 'SCUSDT', 'ZENCASHUSDT',
            
            # Additional Popular
            'ROSEUSDT', 'APEUSDT', 'LDOUSDT', 'WLDUSDT', 'ORDIUSDT',
            'STXUSDT', 'SEIUSDT', 'TIAUSDT', 'BEAMXUSDT', 'PIVXUSDT',
            'RDNTUSDT', 'GASUSDT', 'POLUSDT', 'MASKUSDT', 'LQTYUSDT',
            
            # More DeFi
            'PENDLEUSDT', 'JOEUSDT', 'CVXUSDT', 'FXSUSDT', 'LDOUSDT',
            'AGLDUSDT', 'PERPUSDT', 'RAREUSDT', 'LOKAUSDT', 'BADGERUSDT',
            
            # Solana Ecosystem
            'JUPUSDT', 'JITOUSDT', 'PYTH', 'RAYDIUMUSDT', 'ORCANUSDT',
            
            # Arbitrum Ecosystem  
            'ARBUSDT', 'GMXUSDT', 'MAGICUSDT', 'RDNTUSDT', 'PENDLEUSDT',
            
            # Base Ecosystem
            'BRETTUSDT', 'DEGEN',
            
            # TON Ecosystem
            'TONUSDT', 'NOTUSDT', 'DOGSUSDT',
            
            # Web3 & Social
            'MASKUSDT', 'CYBERUSDT', 'IDUSDT', 'HIGHUSDT', 'VIDTUSDT',
            
            # Chinese Projects
            'NEOUSDT', 'QTUMUSDT', 'ONTUSDT', 'VETUSDT', 'NULSUSDT',
            
            # Korean Projects  
            'ICXUSDT', 'KLAYUSDT', 'METAUSDT',
            
            # Japanese Projects
            'JASMUSDT', 'MONACOINUS',
            
            # Infrastructure & Tools
            'CKBUSDT', 'CFXUSDT', 'BLURUSDT', 'COREUSDT', 'BELUSDT',
            'NMRUSDT', 'NEOUSDT', 'ONGUSDT', 'FXSUSDT', 'CTXCUSDT',
            
            # Newer Launches
            'ACEUSDT', 'NFPUSDT', 'AIUSDT', 'XAIUSDT', 'MANTAUSDT',
            'ALTUSDT', 'JUPTUSDT', 'PYTHUSDT', 'DYMUSDT', 'PIXELUSDT',
            'PORTALUSDT', 'PDAUSDT', 'BOMEUSDT', 'ETHFIUSDT', 'ENAUSDT',
            
            # Legacy but still active
            'XEMUSDT', 'DGBUSDT', 'RVNUSDT', 'SYSUSDT', 'GRSUSDT',
            
            # Additional
            '1000PEPEUSDT', '1000FLOKIUSDT', '1000BONKUSDT', '1000SHIBUSDT',
            '1000LUNCUSDT', '1000XECUSDT',
        ]
        
        # Remove duplicates and sort
        self.symbols = sorted(list(set(self.symbols)))
    
    def get_available_symbols(self):
        """Return list of available symbols"""
        return self.symbols
    
    def get_price(self, exchange, symbol):
        """Get current price from exchange API"""
        # Check cache
        cache_key = f"{exchange}_{symbol}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['time'] < self.cache_duration:
                return cached_data['price']
        
        try:
            price = None
            
            if exchange == 'Binance':
                price = self._get_binance_price(symbol)
            elif exchange == 'CoinEx':
                price = self._get_coinex_price(symbol)
            elif exchange == 'Bybit':
                price = self._get_bybit_price(symbol)
            
            if price:
                self.cache[cache_key] = {
                    'price': price,
                    'time': time.time()
                }
                return price
            
            return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def _get_binance_price(self, symbol):
        """Get price from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
        except:
            pass
        return None
    
    def _get_coinex_price(self, symbol):
        """Get price from CoinEx"""
        try:
            # CoinEx uses different format
            symbol_formatted = symbol.replace('USDT', '_USDT')
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol_formatted}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:
                    return float(data['data']['ticker']['last'])
        except:
            pass
        return None
    
    def _get_bybit_price(self, symbol):
        """Get price from Bybit"""
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['retCode'] == 0 and data['result']['list']:
                    return float(data['result']['list'][0]['lastPrice'])
        except:
            pass
        return None
