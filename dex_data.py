"""
Modul untuk mengambil data dari Decentralized Exchanges (DEX) menggunakan DEX Screener API.
"""

import time
import requests
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from decimal import Decimal
import json
from urllib.parse import urlencode

import config
from utils import retry_on_exception, get_current_timestamp

logger = logging.getLogger("arbitrage.dex")

class DexScreenerAPI:
    """
    Kelas untuk berinteraksi dengan DEX Screener API.
    """
    
    def __init__(self):
        """
        Inisialisasi DEX Screener API.
        """
        self.base_url = config.DEX_SCREENER["base_url"]
        self.rate_limit = config.DEX_SCREENER["rate_limit"]
        self.last_request_time = 0
        self.request_count = 0
        
    def _handle_rate_limit(self):
        """
        Menangani rate limit dengan menunggu jika diperlukan.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Jika waktu sejak permintaan terakhir kurang dari 0.2 detik, tunggu
        # Ini memastikan kita tidak melebihi 300 permintaan per menit
        if time_since_last_request < 0.2:
            time.sleep(0.2 - time_since_last_request)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    @retry_on_exception()
    def _make_request(self, endpoint: str, params: Dict = None) -> Any:
        """
        Membuat permintaan ke DEX Screener API.
        
        Args:
            endpoint: Endpoint API
            params: Parameter permintaan
            
        Returns:
            Respons API
        """
        self._handle_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error saat membuat permintaan ke {url}: {str(e)}")
            raise
    
    @retry_on_exception()
    def search_pairs(self, query: str) -> List[Dict[str, Any]]:
        """
        Mencari pair berdasarkan query.
        
        Args:
            query: Query pencarian
            
        Returns:
            Daftar pair yang cocok
        """
        endpoint = "/latest/dex/search"
        params = {"q": query}
        
        response = self._make_request(endpoint, params)
        
        if "pairs" in response:
            return response["pairs"]
        
        return []
    
    @retry_on_exception()
    def get_pair_by_address(self, chain_id: str, pair_address: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan informasi pair berdasarkan alamat.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            pair_address: Alamat pair
            
        Returns:
            Informasi pair atau None jika tidak ditemukan
        """
        endpoint = f"/latest/dex/pairs/{chain_id}/{pair_address}"
        
        response = self._make_request(endpoint)
        
        if "pairs" in response and len(response["pairs"]) > 0:
            return response["pairs"][0]
        
        return None
    
    @retry_on_exception()
    def get_token_pairs(self, chain_id: str, token_address: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan semua pair untuk token tertentu.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            
        Returns:
            Daftar pair
        """
        endpoint = f"/token-pairs/v1/{chain_id}/{token_address}"
        
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return response
        
        return []
    
    @retry_on_exception()
    def get_token_info(self, chain_id: str, token_address: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan informasi token.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            
        Returns:
            Informasi token
        """
        endpoint = f"/tokens/v1/{chain_id}/{token_address}"
        
        response = self._make_request(endpoint)
        
        if isinstance(response, list):
            return response
        
        return []
    
    def get_token_price(self, chain_id: str, token_address: str, quote_token: str = "USD") -> Optional[Decimal]:
        """
        Mendapatkan harga token dalam quote token.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            quote_token: Token quote (misalnya USD, ETH)
            
        Returns:
            Harga token atau None jika tidak ditemukan
        """
        pairs = self.get_token_pairs(chain_id, token_address)
        
        if not pairs:
            return None
        
        # Cari pair dengan quote token yang sesuai
        for pair in pairs:
            # Jika quote token adalah USD, cari pair dengan priceUsd
            if quote_token == "USD" and "priceUsd" in pair and pair["priceUsd"]:
                return Decimal(pair["priceUsd"])
            
            # Jika quote token bukan USD, cari pair dengan quote token yang sesuai
            if "quoteToken" in pair and "symbol" in pair["quoteToken"]:
                if pair["quoteToken"]["symbol"].upper() == quote_token.upper():
                    if "priceNative" in pair and pair["priceNative"]:
                        return Decimal(pair["priceNative"])
        
        # Jika tidak ada pair yang cocok, gunakan pair pertama
        if "priceUsd" in pairs[0] and pairs[0]["priceUsd"]:
            return Decimal(pairs[0]["priceUsd"])
        
        return None
    
    def get_token_liquidity(self, chain_id: str, token_address: str) -> Optional[Decimal]:
        """
        Mendapatkan likuiditas token dalam USD.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            
        Returns:
            Likuiditas token atau None jika tidak ditemukan
        """
        pairs = self.get_token_pairs(chain_id, token_address)
        
        if not pairs:
            return None
        
        # Hitung total likuiditas dari semua pair
        total_liquidity = Decimal("0")
        
        for pair in pairs:
            if "liquidity" in pair and "usd" in pair["liquidity"]:
                liquidity_usd = pair["liquidity"]["usd"]
                if liquidity_usd:
                    total_liquidity += Decimal(str(liquidity_usd))
        
        return total_liquidity if total_liquidity > 0 else None
    
    def get_best_dex_for_token(self, chain_id: str, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan DEX terbaik untuk token berdasarkan likuiditas.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            
        Returns:
            Informasi DEX terbaik atau None jika tidak ditemukan
        """
        pairs = self.get_token_pairs(chain_id, token_address)
        
        if not pairs:
            return None
        
        # Urutkan pair berdasarkan likuiditas (descending)
        sorted_pairs = sorted(
            pairs,
            key=lambda x: Decimal(str(x["liquidity"]["usd"])) if "liquidity" in x and "usd" in x["liquidity"] and x["liquidity"]["usd"] else Decimal("0"),
            reverse=True
        )
        
        if not sorted_pairs:
            return None
        
        best_pair = sorted_pairs[0]
        
        return {
            "dex_id": best_pair.get("dexId", ""),
            "chain_id": best_pair.get("chainId", ""),
            "pair_address": best_pair.get("pairAddress", ""),
            "liquidity_usd": Decimal(str(best_pair["liquidity"]["usd"])) if "liquidity" in best_pair and "usd" in best_pair["liquidity"] and best_pair["liquidity"]["usd"] else Decimal("0"),
            "price_usd": Decimal(best_pair["priceUsd"]) if "priceUsd" in best_pair and best_pair["priceUsd"] else Decimal("0"),
            "base_token": best_pair.get("baseToken", {}),
            "quote_token": best_pair.get("quoteToken", {})
        }
    
    def get_price_across_dexes(self, chain_id: str, token_address: str) -> List[Dict[str, Any]]:
        """
        Mendapatkan harga token di berbagai DEX.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            
        Returns:
            Daftar harga di berbagai DEX
        """
        pairs = self.get_token_pairs(chain_id, token_address)
        
        if not pairs:
            return []
        
        # Filter pair dengan likuiditas yang cukup (> $10,000)
        filtered_pairs = [
            pair for pair in pairs
            if "liquidity" in pair and "usd" in pair["liquidity"] and pair["liquidity"]["usd"] and Decimal(str(pair["liquidity"]["usd"])) > 10000
        ]
        
        # Buat daftar harga di berbagai DEX
        dex_prices = []
        
        for pair in filtered_pairs:
            dex_info = {
                "dex_id": pair.get("dexId", ""),
                "chain_id": pair.get("chainId", ""),
                "pair_address": pair.get("pairAddress", ""),
                "liquidity_usd": Decimal(str(pair["liquidity"]["usd"])) if "liquidity" in pair and "usd" in pair["liquidity"] and pair["liquidity"]["usd"] else Decimal("0"),
                "price_usd": Decimal(pair["priceUsd"]) if "priceUsd" in pair and pair["priceUsd"] else Decimal("0"),
                "base_token": pair.get("baseToken", {}),
                "quote_token": pair.get("quoteToken", {})
            }
            
            dex_prices.append(dex_info)
        
        return dex_prices
    
    def get_price_across_chains(self, token_symbol: str) -> Dict[str, Dict[str, Any]]:
        """
        Mendapatkan harga token di berbagai chain.
        
        Args:
            token_symbol: Simbol token
            
        Returns:
            Dict dengan chain_id sebagai key dan informasi harga sebagai value
        """
        # Dapatkan alamat token di berbagai chain
        token_addresses = {}
        
        if token_symbol in config.TOKENS_TO_MONITOR:
            token_addresses = config.TOKENS_TO_MONITOR[token_symbol]["address"]
        else:
            # Cari token dengan pencarian
            search_results = self.search_pairs(token_symbol)
            
            for pair in search_results:
                if "baseToken" in pair and "symbol" in pair["baseToken"] and pair["baseToken"]["symbol"].upper() == token_symbol.upper():
                    chain_id = pair.get("chainId", "")
                    token_addresses[chain_id] = pair["baseToken"]["address"]
        
        if not token_addresses:
            return {}
        
        # Dapatkan harga di berbagai chain
        chain_prices = {}
        
        for chain_id, token_address in token_addresses.items():
            best_dex = self.get_best_dex_for_token(chain_id, token_address)
            
            if best_dex:
                chain_prices[chain_id] = best_dex
        
        return chain_prices
    
    def find_arbitrage_opportunities_same_chain(self, chain_id: str, token_address: str, min_price_diff_percentage: float = 0.5) -> List[Dict[str, Any]]:
        """
        Mencari peluang arbitrase di chain yang sama.
        
        Args:
            chain_id: ID chain (misalnya ethereum, bsc)
            token_address: Alamat token
            min_price_diff_percentage: Persentase perbedaan harga minimum
            
        Returns:
            Daftar peluang arbitrase
        """
        dex_prices = self.get_price_across_dexes(chain_id, token_address)
        
        if len(dex_prices) < 2:
            return []
        
        # Cari peluang arbitrase
        opportunities = []
        
        for i in range(len(dex_prices)):
            for j in range(i + 1, len(dex_prices)):
                dex1 = dex_prices[i]
                dex2 = dex_prices[j]
                
                price1 = dex1["price_usd"]
                price2 = dex2["price_usd"]
                
                if price1 == 0 or price2 == 0:
                    continue
                
                # Hitung persentase perbedaan harga
                if price1 > price2:
                    price_diff_percentage = (price1 - price2) / price2 * 100
                    buy_dex = dex2
                    sell_dex = dex1
                else:
                    price_diff_percentage = (price2 - price1) / price1 * 100
                    buy_dex = dex1
                    sell_dex = dex2
                
                # Jika perbedaan harga cukup besar, tambahkan ke peluang arbitrase
                if price_diff_percentage >= min_price_diff_percentage:
                    opportunity = {
                        "type": "same_chain",
                        "chain_id": chain_id,
                        "token_address": token_address,
                        "token_symbol": dex1["base_token"].get("symbol", ""),
                        "buy_dex": buy_dex["dex_id"],
                        "buy_price": buy_dex["price_usd"],
                        "sell_dex": sell_dex["dex_id"],
                        "sell_price": sell_dex["price_usd"],
                        "price_diff_percentage": price_diff_percentage,
                        "buy_liquidity": buy_dex["liquidity_usd"],
                        "sell_liquidity": sell_dex["liquidity_usd"],
                        "timestamp": get_current_timestamp()
                    }
                    
                    opportunities.append(opportunity)
        
        # Urutkan berdasarkan persentase perbedaan harga (descending)
        return sorted(opportunities, key=lambda x: x["price_diff_percentage"], reverse=True)
    
    def find_arbitrage_opportunities_cross_chain(self, token_symbol: str, min_price_diff_percentage: float = 1.0) -> List[Dict[str, Any]]:
        """
        Mencari peluang arbitrase di berbagai chain.
        
        Args:
            token_symbol: Simbol token
            min_price_diff_percentage: Persentase perbedaan harga minimum
            
        Returns:
            Daftar peluang arbitrase
        """
        chain_prices = self.get_price_across_chains(token_symbol)
        
        if len(chain_prices) < 2:
            return []
        
        # Cari peluang arbitrase
        opportunities = []
        
        chains = list(chain_prices.keys())
        
        for i in range(len(chains)):
            for j in range(i + 1, len(chains)):
                chain1 = chains[i]
                chain2 = chains[j]
                
                dex1 = chain_prices[chain1]
                dex2 = chain_prices[chain2]
                
                price1 = dex1["price_usd"]
                price2 = dex2["price_usd"]
                
                if price1 == 0 or price2 == 0:
                    continue
                
                # Hitung persentase perbedaan harga
                if price1 > price2:
                    price_diff_percentage = (price1 - price2) / price2 * 100
                    buy_chain = chain2
                    buy_dex = dex2
                    sell_chain = chain1
                    sell_dex = dex1
                else:
                    price_diff_percentage = (price2 - price1) / price1 * 100
                    buy_chain = chain1
                    buy_dex = dex1
                    sell_chain = chain2
                    sell_dex = dex2
                
                # Jika perbedaan harga cukup besar, tambahkan ke peluang arbitrase
                if price_diff_percentage >= min_price_diff_percentage:
                    # Dapatkan biaya bridge
                    bridge_fee_percentage = 0
                    
                    bridge_key = f"{buy_chain}_to_{sell_chain}"
                    if bridge_key in config.ARBITRAGE_CONFIG["bridge_fees"]:
                        bridge_fee_percentage = config.ARBITRAGE_CONFIG["bridge_fees"][bridge_key]
                    
                    # Hitung keuntungan setelah biaya bridge
                    net_profit_percentage = price_diff_percentage - bridge_fee_percentage
                    
                    if net_profit_percentage > min_price_diff_percentage:
                        opportunity = {
                            "type": "cross_chain",
                            "token_symbol": token_symbol,
                            "buy_chain": buy_chain,
                            "buy_dex": buy_dex["dex_id"],
                            "buy_price": buy_dex["price_usd"],
                            "sell_chain": sell_chain,
                            "sell_dex": sell_dex["dex_id"],
                            "sell_price": sell_dex["price_usd"],
                            "price_diff_percentage": price_diff_percentage,
                            "bridge_fee_percentage": bridge_fee_percentage,
                            "net_profit_percentage": net_profit_percentage,
                            "buy_liquidity": buy_dex["liquidity_usd"],
                            "sell_liquidity": sell_dex["liquidity_usd"],
                            "timestamp": get_current_timestamp()
                        }
                        
                        opportunities.append(opportunity)
        
        # Urutkan berdasarkan persentase keuntungan bersih (descending)
        return sorted(opportunities, key=lambda x: x["net_profit_percentage"], reverse=True)
    
    def get_top_gainers(self, chain_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar top gainers.
        
        Args:
            chain_id: ID chain (opsional, jika None akan mencari di semua chain)
            limit: Jumlah top gainers
            
        Returns:
            Daftar top gainers
        """
        # Sayangnya, DEX Screener API tidak menyediakan endpoint khusus untuk top gainers
        # Kita bisa menggunakan pencarian dengan query kosong dan mengurutkan hasilnya
        # Namun, ini tidak efisien dan mungkin tidak akurat
        
        # Sebagai alternatif, kita bisa mencari token populer
        popular_tokens = ["ETH", "BTC", "BNB", "MATIC", "LINK", "UNI", "AAVE", "SNX", "COMP", "MKR"]
        
        results = []
        
        for token in popular_tokens:
            search_results = self.search_pairs(token)
            
            for pair in search_results:
                if chain_id and pair.get("chainId") != chain_id:
                    continue
                
                if "priceChange" in pair and "h24" in pair["priceChange"] and pair["priceChange"]["h24"]:
                    price_change_24h = Decimal(str(pair["priceChange"]["h24"]))
                    
                    if price_change_24h > 0:
                        result = {
                            "chain_id": pair.get("chainId", ""),
                            "dex_id": pair.get("dexId", ""),
                            "pair_address": pair.get("pairAddress", ""),
                            "base_token": pair.get("baseToken", {}),
                            "quote_token": pair.get("quoteToken", {}),
                            "price_usd": Decimal(pair["priceUsd"]) if "priceUsd" in pair and pair["priceUsd"] else Decimal("0"),
                            "price_change_24h": price_change_24h,
                            "liquidity_usd": Decimal(str(pair["liquidity"]["usd"])) if "liquidity" in pair and "usd" in pair["liquidity"] and pair["liquidity"]["usd"] else Decimal("0"),
                        }
                        
                        results.append(result)
        
        # Urutkan berdasarkan persentase perubahan harga (descending)
        sorted_results = sorted(results, key=lambda x: x["price_change_24h"], reverse=True)
        
        # Ambil top N
        return sorted_results[:limit]

# Singleton instance
dex_screener_api = DexScreenerAPI()
