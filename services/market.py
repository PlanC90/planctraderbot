from typing import Dict
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _create_session():
    """Optimized requests session with retry logic"""
    session = requests.Session()
    retries = Retry(
        total=2,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class MarketService:
    def __init__(self):
        self.latest_changes: Dict[str, float] = {}
        self.latest_prices: Dict[str, float] = {}
        self._last_coinpaprika_fetch = 0.0
        self._coinpaprika_cache = {}
        self._binance_price_cache = {}
        self._last_binance_price_fetch = 0.0
        self._coinpaprika_failed = False
        self.session = _create_session()

    def fetch_futures_1h(self, symbols: list, timeout: int = 10) -> None:
        """
        1 saatlik değişimleri hesapla - CoinPaprika API ile (Binance fallback)
        
        ÖNCELIK 1: CoinPaprika (60sn cache, API limit korumalı)
        FALLBACK: Binance klines (CoinPaprika çalışmazsa)
        """
        changes: Dict[str, float] = {}
        prices: Dict[str, float] = {}
        
        try:
            now = time.time()
            
            # 🔥 COINPAPRIKA - 60 saniyede bir güncelle (API limit koruması)
            if now - self._last_coinpaprika_fetch > 60:
                try:
                    # CoinPaprika'dan TÜM coin verilerini tek istekte çek
                    url = "https://api.coinpaprika.com/v1/tickers"
                    params = {"quotes": "USD"}
                    headers = {"User-Agent": "BinanceFuturesBot/2.0"}
                    
                    resp = self.session.get(url, params=params, headers=headers, timeout=timeout)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        # Symbol bazlı cache oluştur
                        self._coinpaprika_cache = {}
                        for item in data:
                            symbol = item.get('symbol', '').upper()
                            if symbol:
                                # USDT suffix'li ve suffix'siz versiyonları kaydet
                                self._coinpaprika_cache[symbol] = {
                                    'percent_change_1h': item.get('quotes', {}).get('USD', {}).get('percent_change_1h', 0.0),
                                    'price': item.get('quotes', {}).get('USD', {}).get('price', 0.0)
                                }
                                self._coinpaprika_cache[f"{symbol}USDT"] = self._coinpaprika_cache[symbol]
                        
                        self._last_coinpaprika_fetch = now
                        self._coinpaprika_failed = False  # Başarılı oldu
                        
                except Exception as e:
                    # CoinPaprika başarısız - fallback bayrağı
                    self._coinpaprika_failed = True
            
            # 🔄 BINANCE FALLBACK - CoinPaprika cache boşsa veya başarısız olduysa
            if not self._coinpaprika_cache or self._coinpaprika_failed:
                # Binance'tan 1h değişimlerini çek
                self._fetch_binance_1h_changes(symbols[:100], timeout)
            
            # Binance'tan fiyat verisi (her durumda) - 30 saniye cache
            if now - self._last_binance_price_fetch > 30:
                try:
                    url_binance = "https://fapi.binance.com/fapi/v1/ticker/price"
                    resp_binance = self.session.get(url_binance, timeout=timeout)
                    if resp_binance.status_code == 200:
                        binance_data = resp_binance.json()
                        self._binance_price_cache = {
                            item['symbol']: float(item['price']) 
                            for item in binance_data if 'symbol' in item and 'price' in item
                        }
                        self._last_binance_price_fetch = now
                except Exception:
                    pass
            
            # İstenen semboller için verileri hazırla
            for symbol in symbols:
                # Önce CoinPaprika cache'den dene
                if symbol in self._coinpaprika_cache:
                    cache_data = self._coinpaprika_cache[symbol]
                    changes[symbol] = cache_data['percent_change_1h'] or 0.0
                    prices[symbol] = cache_data['price'] or 0.0
                    
                    # Fiyat yoksa Binance'tan al
                    if prices[symbol] == 0.0 and symbol in self._binance_price_cache:
                        prices[symbol] = self._binance_price_cache[symbol]
                
                # Cache'de yoksa Binance fallback
                elif symbol in self._binance_price_cache:
                    prices[symbol] = self._binance_price_cache[symbol]
                    changes[symbol] = 0.0  # Değişim verisi yok
                
        except Exception as e:
            # Tamamen hata olursa mevcut cache'i kullan
            for symbol in symbols:
                if symbol in self._coinpaprika_cache:
                    cache_data = self._coinpaprika_cache[symbol]
                    changes[symbol] = cache_data['percent_change_1h'] or 0.0
                    prices[symbol] = cache_data['price'] or 0.0
                elif symbol in self._binance_price_cache:
                    prices[symbol] = self._binance_price_cache[symbol]
                    changes[symbol] = 0.0
        
        self.latest_changes = changes
        self.latest_prices = prices
    
    def _fetch_binance_1h_changes(self, symbols: list, timeout: int = 10) -> None:
        """
        Binance Futures'tan 1 saatlik değişimleri çek (FALLBACK)
        CoinPaprika çalışmazsa bu devreye girer
        """
        try:
            # Paralel istekler ile hızlandırma (max 20 coin aynı anda)
            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_symbol = {
                    executor.submit(self._fetch_symbol_1h_kline, symbol, timeout): symbol 
                    for symbol in symbols[:100]  # Max 100 coin
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        if result:
                            change_percent, current_price = result
                            # CoinPaprika cache formatında kaydet (uyumluluk için)
                            base_symbol = symbol.replace('USDT', '').replace('USDC', '')
                            self._coinpaprika_cache[symbol] = {
                                'percent_change_1h': change_percent,
                                'price': current_price
                            }
                            self._coinpaprika_cache[base_symbol] = self._coinpaprika_cache[symbol]
                    except Exception:
                        continue
                        
        except Exception as e:
            pass
    
    def _fetch_symbol_1h_kline(self, symbol: str, timeout: int = 5):
        """Tek bir sembol için Binance 1h kline verisi çek"""
        try:
            url = "https://fapi.binance.com/fapi/v1/klines"
            params = {
                'symbol': symbol,
                'interval': '1h',
                'limit': 2  # Son 2 saat
            }
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            
            if len(data) >= 2:
                current_close = float(data[1][4])  # Son saat kapanış
                previous_close = float(data[0][4])  # Önceki saat kapanış
                
                # 1 saatlik değişim yüzdesi
                change_percent = ((current_close - previous_close) / previous_close) * 100
                return (change_percent, current_close)
        except Exception:
            pass
        return None


