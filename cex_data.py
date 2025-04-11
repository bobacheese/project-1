"""
Modul untuk mengambil data dari Centralized Exchanges (CEX).
"""

import time
import hmac
import hashlib
import requests
import logging
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
import json
from urllib.parse import urlencode

import config
from utils import retry_on_exception, get_current_timestamp

logger = logging.getLogger("arbitrage.cex")

class CEXDataProvider:
    """
    Kelas dasar untuk penyedia data CEX.
    """
    
    def __init__(self, exchange_name: str):
        """
        Inisialisasi penyedia data CEX.
        
        Args:
            exchange_name: Nama exchange
        """
        self.exchange_name = exchange_name
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset = 0
        
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Mendapatkan data ticker untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            
        Returns:
            Data ticker
        """
        raise NotImplementedError("Metode ini harus diimplementasikan oleh subclass")
    
    def get_orderbook(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """
        Mendapatkan data order book untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            limit: Jumlah level harga
            
        Returns:
            Data order book
        """
        raise NotImplementedError("Metode ini harus diimplementasikan oleh subclass")
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Mendapatkan data perdagangan terbaru untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            limit: Jumlah perdagangan
            
        Returns:
            Daftar perdagangan terbaru
        """
        raise NotImplementedError("Metode ini harus diimplementasikan oleh subclass")
    
    def get_top_gainers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar top gainers.
        
        Args:
            limit: Jumlah top gainers
            
        Returns:
            Daftar top gainers
        """
        raise NotImplementedError("Metode ini harus diimplementasikan oleh subclass")
    
    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan data ticker untuk semua simbol.
        
        Returns:
            Daftar data ticker
        """
        raise NotImplementedError("Metode ini harus diimplementasikan oleh subclass")
    
    def _handle_rate_limit(self):
        """
        Menangani rate limit dengan menunggu jika diperlukan.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Jika waktu sejak permintaan terakhir kurang dari 1 detik, tunggu
        if time_since_last_request < 1:
            time.sleep(1 - time_since_last_request)
        
        self.last_request_time = time.time()
        self.request_count += 1

class BinanceDataProvider(CEXDataProvider):
    """
    Penyedia data untuk Binance.
    """
    
    def __init__(self):
        """
        Inisialisasi penyedia data Binance.
        """
        super().__init__("binance")
        self.base_url = config.CEX_LIST["binance"]["base_url"]
        self.api_key = config.CEX_LIST["binance"]["api_key"]
        self.api_secret = config.CEX_LIST["binance"]["api_secret"]
        self.weight_limit = config.CEX_LIST["binance"]["weight_limit"]
        
    def _generate_signature(self, query_string: str) -> str:
        """
        Menghasilkan tanda tangan untuk permintaan API yang memerlukan autentikasi.
        
        Args:
            query_string: String query
            
        Returns:
            Tanda tangan
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @retry_on_exception()
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, signed: bool = False) -> Any:
        """
        Membuat permintaan ke API Binance.
        
        Args:
            endpoint: Endpoint API
            method: Metode HTTP
            params: Parameter permintaan
            signed: Apakah permintaan memerlukan tanda tangan
            
        Returns:
            Respons API
        """
        self._handle_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key
        
        if params is None:
            params = {}
        
        if signed:
            params["timestamp"] = get_current_timestamp()
            query_string = urlencode(params)
            params["signature"] = self._generate_signature(query_string)
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, params=params, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Metode HTTP tidak didukung: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error saat membuat permintaan ke {url}: {str(e)}")
            raise
    
    @retry_on_exception()
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Mendapatkan data ticker untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            
        Returns:
            Data ticker
        """
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        
        return self._make_request(endpoint, params=params)
    
    @retry_on_exception()
    def get_orderbook(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """
        Mendapatkan data order book untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            limit: Jumlah level harga
            
        Returns:
            Data order book
        """
        endpoint = "/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}
        
        return self._make_request(endpoint, params=params)
    
    @retry_on_exception()
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Mendapatkan data perdagangan terbaru untuk simbol tertentu.
        
        Args:
            symbol: Simbol trading
            limit: Jumlah perdagangan
            
        Returns:
            Daftar perdagangan terbaru
        """
        endpoint = "/api/v3/trades"
        params = {"symbol": symbol, "limit": limit}
        
        return self._make_request(endpoint, params=params)
    
    @retry_on_exception()
    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan data ticker untuk semua simbol.
        
        Returns:
            Daftar data ticker
        """
        endpoint = "/api/v3/ticker/price"
        
        return self._make_request(endpoint)
    
    @retry_on_exception()
    def get_top_gainers(self, limit: int = 20, quote_asset: str = "USDT") -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar top gainers.
        
        Args:
            limit: Jumlah top gainers
            quote_asset: Aset quote (misalnya USDT, BTC)
            
        Returns:
            Daftar top gainers
        """
        # Dapatkan semua ticker 24 jam
        endpoint = "/api/v3/ticker/24hr"
        all_tickers = self._make_request(endpoint)
        
        # Filter ticker dengan quote asset yang ditentukan
        filtered_tickers = [
            ticker for ticker in all_tickers 
            if ticker["symbol"].endswith(quote_asset) and float(ticker["priceChangePercent"]) > 0
        ]
        
        # Urutkan berdasarkan persentase perubahan harga (descending)
        sorted_tickers = sorted(
            filtered_tickers, 
            key=lambda x: float(x["priceChangePercent"]), 
            reverse=True
        )
        
        # Ambil top N
        return sorted_tickers[:limit]
    
    @retry_on_exception()
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Mendapatkan informasi exchange.
        
        Returns:
            Informasi exchange
        """
        endpoint = "/api/v3/exchangeInfo"
        
        return self._make_request(endpoint)
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan informasi simbol.
        
        Args:
            symbol: Simbol trading
            
        Returns:
            Informasi simbol atau None jika tidak ditemukan
        """
        exchange_info = self.get_exchange_info()
        
        for symbol_info in exchange_info["symbols"]:
            if symbol_info["symbol"] == symbol:
                return symbol_info
        
        return None
    
    def format_symbol(self, base_asset: str, quote_asset: str) -> str:
        """
        Format simbol trading untuk Binance.
        
        Args:
            base_asset: Aset dasar
            quote_asset: Aset quote
            
        Returns:
            Simbol trading
        """
        return f"{base_asset}{quote_asset}"
    
    def get_price(self, symbol: str) -> Decimal:
        """
        Mendapatkan harga terbaru untuk simbol.
        
        Args:
            symbol: Simbol trading
            
        Returns:
            Harga terbaru
        """
        ticker = self.get_ticker(symbol)
        return Decimal(ticker["lastPrice"])
    
    def get_bid_ask(self, symbol: str) -> Dict[str, Decimal]:
        """
        Mendapatkan harga bid dan ask terbaik untuk simbol.
        
        Args:
            symbol: Simbol trading
            
        Returns:
            Dict dengan bid dan ask
        """
        orderbook = self.get_orderbook(symbol, limit=5)
        
        if not orderbook["bids"] or not orderbook["asks"]:
            return {"bid": Decimal("0"), "ask": Decimal("0")}
        
        return {
            "bid": Decimal(orderbook["bids"][0][0]),
            "ask": Decimal(orderbook["asks"][0][0])
        }

# Factory untuk membuat instance penyedia data CEX
def get_cex_data_provider(exchange_name: str) -> CEXDataProvider:
    """
    Mendapatkan instance penyedia data CEX.
    
    Args:
        exchange_name: Nama exchange
        
    Returns:
        Instance penyedia data CEX
    """
    if exchange_name.lower() == "binance":
        return BinanceDataProvider()
    else:
        raise ValueError(f"Exchange tidak didukung: {exchange_name}")
