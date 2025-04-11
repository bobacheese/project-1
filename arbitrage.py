"""
Modul untuk logika arbitrase cryptocurrency.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from decimal import Decimal
import json
from datetime import datetime

import config
from utils import (
    calculate_price_difference_percentage,
    calculate_profit_after_fees,
    is_profitable_opportunity,
    estimate_gas_cost,
    get_bridge_fee,
    get_token_address,
    is_token_multichain,
    get_networks_for_token
)
from cex_data import get_cex_data_provider
from dex_data import dex_screener_api

logger = logging.getLogger("arbitrage.logic")

class ArbitrageScanner:
    """
    Kelas untuk mencari peluang arbitrase.
    """

    def __init__(self):
        """
        Inisialisasi scanner arbitrase.
        """
        self.binance = get_cex_data_provider("binance")
        self.dex_screener = dex_screener_api
        self.min_profit_percentage = config.ARBITRAGE_CONFIG["min_profit_percentage"]
        self.min_liquidity = 10000  # Default likuiditas minimum: $10,000

    def scan_scenario_1(self, top_gainers_limit: int = 20) -> List[Dict[str, Any]]:
        """
        Mencari peluang arbitrase untuk Skenario 1 (DEX - CEX, Sama Jaringan).

        Args:
            top_gainers_limit: Jumlah top gainers yang akan dipantau

        Returns:
            Daftar peluang arbitrase
        """
        logger.info("Memulai pemindaian untuk Skenario 1 (DEX - CEX, Sama Jaringan)")

        opportunities = []

        # Dapatkan top gainers dari Binance
        try:
            top_gainers = self.binance.get_top_gainers(limit=top_gainers_limit)
            logger.info(f"Berhasil mendapatkan {len(top_gainers)} top gainers dari Binance")
        except Exception as e:
            logger.error(f"Gagal mendapatkan top gainers dari Binance: {str(e)}")
            return opportunities

        # Periksa setiap top gainer
        for gainer in top_gainers:
            try:
                # Dapatkan simbol dan harga di Binance
                symbol = gainer["symbol"]
                base_asset = ""
                quote_asset = ""

                # Ekstrak base asset dan quote asset dari simbol
                for quote in ["USDT", "BUSD", "BTC", "ETH", "BNB"]:
                    if symbol.endswith(quote):
                        base_asset = symbol[:-len(quote)]
                        quote_asset = quote
                        break

                if not base_asset or not quote_asset:
                    logger.warning(f"Tidak dapat mengekstrak base asset dan quote asset dari simbol {symbol}")
                    continue

                # Dapatkan harga di Binance
                binance_price = Decimal(gainer["lastPrice"])

                logger.info(f"Memeriksa {base_asset} dengan harga Binance {binance_price} {quote_asset}")

                # Dapatkan alamat token di berbagai jaringan
                token_networks = {}

                if base_asset in config.TOKENS_TO_MONITOR:
                    token_networks = config.TOKENS_TO_MONITOR[base_asset]["address"]

                if not token_networks:
                    logger.warning(f"Tidak ada alamat token yang dikonfigurasi untuk {base_asset}")
                    continue

                # Periksa harga di DEX di setiap jaringan
                for network, token_address in token_networks.items():
                    try:
                        # Dapatkan harga di DEX
                        dex_prices = self.dex_screener.get_price_across_dexes(network, token_address)

                        if not dex_prices:
                            logger.warning(f"Tidak ada data harga DEX untuk {base_asset} di jaringan {network}")
                            continue

                        # Periksa setiap DEX
                        for dex_info in dex_prices:
                            dex_id = dex_info["dex_id"]
                            dex_price_usd = dex_info["price_usd"]

                            # Konversi harga Binance ke USD jika perlu
                            binance_price_usd = binance_price

                            if quote_asset != "USDT" and quote_asset != "BUSD":
                                # Dapatkan harga quote asset dalam USD
                                quote_ticker = self.binance.get_ticker(f"{quote_asset}USDT")
                                quote_price_usd = Decimal(quote_ticker["lastPrice"])
                                binance_price_usd = binance_price * quote_price_usd

                            # Hitung perbedaan harga
                            if binance_price_usd > dex_price_usd:
                                # Beli di DEX, jual di Binance
                                price_diff_percentage = calculate_price_difference_percentage(dex_price_usd, binance_price_usd)
                                buy_platform = f"{dex_id} ({network})"
                                buy_price = dex_price_usd
                                sell_platform = "Binance"
                                sell_price = binance_price_usd
                            else:
                                # Beli di Binance, jual di DEX
                                price_diff_percentage = calculate_price_difference_percentage(binance_price_usd, dex_price_usd)
                                buy_platform = "Binance"
                                buy_price = binance_price_usd
                                sell_platform = f"{dex_id} ({network})"
                                sell_price = dex_price_usd

                            # Dapatkan biaya transaksi
                            if buy_platform == "Binance":
                                buy_fee_percentage = config.ARBITRAGE_CONFIG["transaction_fees"]["binance"]["taker"]
                            else:
                                buy_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(dex_id.lower(), 0.3)

                            if sell_platform == "Binance":
                                sell_fee_percentage = config.ARBITRAGE_CONFIG["transaction_fees"]["binance"]["taker"]
                            else:
                                sell_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(dex_id.lower(), 0.3)

                            # Perkiraan biaya gas
                            gas_cost = estimate_gas_cost(network)

                            # Hitung keuntungan setelah biaya
                            amount = Decimal("1")  # Jumlah token untuk simulasi
                            net_profit, profit_percentage = calculate_profit_after_fees(
                                buy_price=buy_price,
                                sell_price=sell_price,
                                amount=amount,
                                buy_fee_percentage=buy_fee_percentage,
                                sell_fee_percentage=sell_fee_percentage,
                                gas_cost=gas_cost
                            )

                            # Periksa likuiditas
                            liquidity = float(dex_info["liquidity_usd"]) if "liquidity_usd" in dex_info else 0

                            # Jika menguntungkan dan likuiditas cukup, tambahkan ke daftar peluang
                            if is_profitable_opportunity(profit_percentage, self.min_profit_percentage) and liquidity >= self.min_liquidity:
                                opportunity = {
                                    "scenario": 1,
                                    "token": base_asset,
                                    "buy_platform": buy_platform,
                                    "buy_price": float(buy_price),
                                    "sell_platform": sell_platform,
                                    "sell_price": float(sell_price),
                                    "price_diff_percentage": float(price_diff_percentage),
                                    "buy_fee_percentage": float(buy_fee_percentage),
                                    "sell_fee_percentage": float(sell_fee_percentage),
                                    "gas_cost": float(gas_cost),
                                    "net_profit": float(net_profit),
                                    "profit_percentage": float(profit_percentage),
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "network": network,
                                    "token_address": token_address,
                                    "liquidity": float(dex_info["liquidity_usd"]) if "liquidity_usd" in dex_info else 0
                                }

                                opportunities.append(opportunity)
                                logger.info(f"Peluang arbitrase ditemukan untuk {base_asset}: {buy_platform} -> {sell_platform}, profit {profit_percentage:.2f}%")

                    except Exception as e:
                        logger.error(f"Error saat memeriksa {base_asset} di jaringan {network}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error saat memproses top gainer {gainer['symbol']}: {str(e)}")
                continue

        # Urutkan berdasarkan persentase keuntungan (descending)
        opportunities.sort(key=lambda x: x["profit_percentage"], reverse=True)

        logger.info(f"Pemindaian Skenario 1 selesai. Ditemukan {len(opportunities)} peluang arbitrase.")

        return opportunities

    def scan_scenario_2(self, tokens_to_check: List[str] = None) -> List[Dict[str, Any]]:
        """
        Mencari peluang arbitrase untuk Skenario 2 (DEX - DEX, Sama Jaringan).

        Args:
            tokens_to_check: Daftar token yang akan diperiksa (jika None, gunakan dari konfigurasi)

        Returns:
            Daftar peluang arbitrase
        """
        logger.info("Memulai pemindaian untuk Skenario 2 (DEX - DEX, Sama Jaringan)")

        opportunities = []

        # Jika tidak ada daftar token yang diberikan, gunakan dari konfigurasi
        if tokens_to_check is None:
            tokens_to_check = list(config.TOKENS_TO_MONITOR.keys())

        # Periksa setiap token
        for token in tokens_to_check:
            try:
                logger.info(f"Memeriksa token {token} untuk peluang arbitrase DEX-DEX")

                # Dapatkan alamat token di berbagai jaringan
                token_networks = {}

                if token in config.TOKENS_TO_MONITOR:
                    token_networks = config.TOKENS_TO_MONITOR[token]["address"]

                if not token_networks:
                    logger.warning(f"Tidak ada alamat token yang dikonfigurasi untuk {token}")
                    continue

                # Periksa setiap jaringan
                for network, token_address in token_networks.items():
                    try:
                        # Tambahkan logging untuk melihat data mentah
                        logger.info(f"Mengambil data harga untuk {token} di jaringan {network}")

                        # Dapatkan data harga dari berbagai DEX
                        dex_prices = self.dex_screener.get_price_across_dexes(network, token_address)

                        # Log jumlah DEX dan rentang harga
                        if dex_prices:
                            min_price = min([p["price_usd"] for p in dex_prices if p["price_usd"] > 0], default=0)
                            max_price = max([p["price_usd"] for p in dex_prices if p["price_usd"] > 0], default=0)
                            price_diff_pct = 0
                            if min_price > 0:
                                price_diff_pct = ((max_price - min_price) / min_price) * 100

                            logger.info(f"Data {token} di {network}: {len(dex_prices)} DEX, harga min: {min_price}, max: {max_price}, diff: {price_diff_pct:.2f}%")

                            # Log detail DEX dengan harga tertinggi dan terendah
                            if len(dex_prices) > 1:
                                min_dex = min(dex_prices, key=lambda x: x["price_usd"] if x["price_usd"] > 0 else float('inf'))
                                max_dex = max(dex_prices, key=lambda x: x["price_usd"] if x["price_usd"] > 0 else 0)
                                logger.info(f"DEX dengan harga terendah: {min_dex['dex_id']} ({min_dex['price_usd']}), tertinggi: {max_dex['dex_id']} ({max_dex['price_usd']})")
                        else:
                            logger.warning(f"Tidak ada data harga yang ditemukan untuk {token} di jaringan {network}")

                        # Cari peluang arbitrase di jaringan yang sama
                        same_chain_opportunities = self.dex_screener.find_arbitrage_opportunities_same_chain(
                            chain_id=network,
                            token_address=token_address,
                            min_price_diff_percentage=self.min_profit_percentage
                        )

                        if not same_chain_opportunities:
                            logger.info(f"Tidak ada peluang arbitrase untuk {token} di jaringan {network} yang memenuhi minimum profit {self.min_profit_percentage}%")
                            continue

                        # Proses setiap peluang
                        for opp in same_chain_opportunities:
                            try:
                                # Dapatkan biaya transaksi
                                buy_dex = opp["buy_dex"]
                                sell_dex = opp["sell_dex"]

                                buy_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(buy_dex.lower(), 0.3)
                                sell_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(sell_dex.lower(), 0.3)

                                # Perkiraan biaya gas
                                gas_cost = estimate_gas_cost(network)

                                # Hitung keuntungan setelah biaya
                                amount = Decimal("1")  # Jumlah token untuk simulasi
                                net_profit, profit_percentage = calculate_profit_after_fees(
                                    buy_price=opp["buy_price"],
                                    sell_price=opp["sell_price"],
                                    amount=amount,
                                    buy_fee_percentage=buy_fee_percentage,
                                    sell_fee_percentage=sell_fee_percentage,
                                    gas_cost=gas_cost
                                )

                                # Periksa likuiditas
                                buy_liquidity = float(opp["buy_liquidity"]) if "buy_liquidity" in opp else 0
                                sell_liquidity = float(opp["sell_liquidity"]) if "sell_liquidity" in opp else 0
                                min_liquidity = min(buy_liquidity, sell_liquidity)

                                # Jika menguntungkan dan likuiditas cukup, tambahkan ke daftar peluang
                                if is_profitable_opportunity(profit_percentage, self.min_profit_percentage) and min_liquidity >= self.min_liquidity:
                                    opportunity = {
                                        "scenario": 2,
                                        "token": token,
                                        "buy_platform": f"{buy_dex} ({network})",
                                        "buy_price": float(opp["buy_price"]),
                                        "sell_platform": f"{sell_dex} ({network})",
                                        "sell_price": float(opp["sell_price"]),
                                        "price_diff_percentage": float(opp["price_diff_percentage"]),
                                        "buy_fee_percentage": float(buy_fee_percentage),
                                        "sell_fee_percentage": float(sell_fee_percentage),
                                        "gas_cost": float(gas_cost),
                                        "net_profit": float(net_profit),
                                        "profit_percentage": float(profit_percentage),
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "network": network,
                                        "token_address": token_address,
                                        "buy_liquidity": float(opp["buy_liquidity"]),
                                        "sell_liquidity": float(opp["sell_liquidity"])
                                    }

                                    opportunities.append(opportunity)
                                    logger.info(f"Peluang arbitrase ditemukan untuk {token}: {buy_dex} -> {sell_dex}, profit {profit_percentage:.2f}%")

                            except Exception as e:
                                logger.error(f"Error saat memproses peluang arbitrase untuk {token} di {network}: {str(e)}")
                                continue

                    except Exception as e:
                        logger.error(f"Error saat memeriksa {token} di jaringan {network}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error saat memproses token {token}: {str(e)}")
                continue

        # Urutkan berdasarkan persentase keuntungan (descending)
        opportunities.sort(key=lambda x: x["profit_percentage"], reverse=True)

        logger.info(f"Pemindaian Skenario 2 selesai. Ditemukan {len(opportunities)} peluang arbitrase.")

        return opportunities

    def scan_scenario_3(self, tokens_to_check: List[str] = None) -> List[Dict[str, Any]]:
        """
        Mencari peluang arbitrase untuk Skenario 3 (DEX - DEX, Beda Jaringan).

        Args:
            tokens_to_check: Daftar token yang akan diperiksa (jika None, gunakan dari konfigurasi)

        Returns:
            Daftar peluang arbitrase
        """
        logger.info("Memulai pemindaian untuk Skenario 3 (DEX - DEX, Beda Jaringan)")

        opportunities = []

        # Jika tidak ada daftar token yang diberikan, gunakan dari konfigurasi
        if tokens_to_check is None:
            # Filter hanya token multichain
            tokens_to_check = [
                token for token in config.TOKENS_TO_MONITOR.keys()
                if is_token_multichain(token)
            ]

        # Periksa setiap token
        for token in tokens_to_check:
            try:
                logger.info(f"Memeriksa token {token} untuk peluang arbitrase DEX-DEX beda jaringan")

                # Cari peluang arbitrase di berbagai jaringan
                cross_chain_opportunities = self.dex_screener.find_arbitrage_opportunities_cross_chain(
                    token_symbol=token,
                    min_price_diff_percentage=self.min_profit_percentage
                )

                if not cross_chain_opportunities:
                    logger.info(f"Tidak ada peluang arbitrase cross-chain untuk {token}")
                    continue

                # Proses setiap peluang
                for opp in cross_chain_opportunities:
                    try:
                        # Dapatkan biaya transaksi
                        buy_dex = opp["buy_dex"]
                        sell_dex = opp["sell_dex"]
                        buy_chain = opp["buy_chain"]
                        sell_chain = opp["sell_chain"]

                        buy_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(buy_dex.lower(), 0.3)
                        sell_fee_percentage = config.ARBITRAGE_CONFIG["dex_fees"].get(sell_dex.lower(), 0.3)

                        # Perkiraan biaya gas untuk kedua jaringan
                        buy_gas_cost = estimate_gas_cost(buy_chain)
                        sell_gas_cost = estimate_gas_cost(sell_chain)
                        total_gas_cost = buy_gas_cost + sell_gas_cost

                        # Biaya bridge
                        bridge_fee_percentage = opp["bridge_fee_percentage"]

                        # Hitung keuntungan setelah biaya
                        amount = Decimal("1")  # Jumlah token untuk simulasi

                        # Biaya bridge dihitung sebagai persentase dari jumlah token
                        bridge_fee = amount * (Decimal(str(bridge_fee_percentage)) / Decimal("100"))
                        amount_after_bridge = amount - bridge_fee

                        net_profit, profit_percentage = calculate_profit_after_fees(
                            buy_price=opp["buy_price"],
                            sell_price=opp["sell_price"],
                            amount=amount_after_bridge,  # Jumlah setelah biaya bridge
                            buy_fee_percentage=buy_fee_percentage,
                            sell_fee_percentage=sell_fee_percentage,
                            gas_cost=total_gas_cost,
                            other_fees=Decimal("0")  # Biaya bridge sudah diperhitungkan dalam amount_after_bridge
                        )

                        # Periksa likuiditas
                        buy_liquidity = float(opp["buy_liquidity"]) if "buy_liquidity" in opp else 0
                        sell_liquidity = float(opp["sell_liquidity"]) if "sell_liquidity" in opp else 0
                        min_liquidity = min(buy_liquidity, sell_liquidity)

                        # Jika menguntungkan dan likuiditas cukup, tambahkan ke daftar peluang
                        if is_profitable_opportunity(profit_percentage, self.min_profit_percentage) and min_liquidity >= self.min_liquidity:
                            opportunity = {
                                "scenario": 3,
                                "token": token,
                                "buy_platform": f"{buy_dex} ({buy_chain})",
                                "buy_price": float(opp["buy_price"]),
                                "sell_platform": f"{sell_dex} ({sell_chain})",
                                "sell_price": float(opp["sell_price"]),
                                "price_diff_percentage": float(opp["price_diff_percentage"]),
                                "buy_fee_percentage": float(buy_fee_percentage),
                                "sell_fee_percentage": float(sell_fee_percentage),
                                "bridge_fee_percentage": float(bridge_fee_percentage),
                                "gas_cost": float(total_gas_cost),
                                "net_profit": float(net_profit),
                                "profit_percentage": float(profit_percentage),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "buy_chain": buy_chain,
                                "sell_chain": sell_chain,
                                "buy_liquidity": float(opp["buy_liquidity"]),
                                "sell_liquidity": float(opp["sell_liquidity"])
                            }

                            opportunities.append(opportunity)
                            logger.info(f"Peluang arbitrase cross-chain ditemukan untuk {token}: {buy_dex} ({buy_chain}) -> {sell_dex} ({sell_chain}), profit {profit_percentage:.2f}%")

                    except Exception as e:
                        logger.error(f"Error saat memproses peluang arbitrase cross-chain untuk {token}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error saat memproses token {token} untuk arbitrase cross-chain: {str(e)}")
                continue

        # Urutkan berdasarkan persentase keuntungan (descending)
        opportunities.sort(key=lambda x: x["profit_percentage"], reverse=True)

        logger.info(f"Pemindaian Skenario 3 selesai. Ditemukan {len(opportunities)} peluang arbitrase.")

        return opportunities

    def scan_all_scenarios(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Mencari peluang arbitrase untuk semua skenario.

        Returns:
            Dict dengan skenario sebagai key dan daftar peluang sebagai value
        """
        logger.info("Memulai pemindaian untuk semua skenario arbitrase")

        results = {}

        # Skenario 1: DEX - CEX, Sama Jaringan
        results[1] = self.scan_scenario_1()

        # Skenario 2: DEX - DEX, Sama Jaringan
        results[2] = self.scan_scenario_2()

        # Skenario 3: DEX - DEX, Beda Jaringan
        results[3] = self.scan_scenario_3()

        logger.info("Pemindaian semua skenario selesai")

        return results

# Singleton instance
arbitrage_scanner = ArbitrageScanner()
