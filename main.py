"""
Entry point untuk program arbitrase cryptocurrency.
"""

import argparse
import logging
import time
import sys
from typing import Dict, Any, List, Optional
import re

import config
from arbitrage import arbitrage_scanner
from output import display_results
from utils import logger

def get_tokens_by_category(category: str) -> List[str]:
    """
    Mendapatkan daftar token berdasarkan kategori.

    Args:
        category: Kategori token (wrapped, stablecoins, defi, gaming, layer2, all)

    Returns:
        Daftar token dalam kategori tersebut
    """
    all_tokens = list(config.TOKENS_TO_MONITOR.keys())

    if category == "all":
        return all_tokens

    # Kategori token berdasarkan prefiks atau pola nama
    categories = {
        "wrapped": ["WETH", "WBTC", "WBNB", "WMATIC"],
        "stablecoins": ["USDT", "USDC", "DAI", "BUSD", "FRAX"],
        "defi": [
            # Original DeFi tokens
            "LINK", "UNI", "AAVE", "SUSHI", "CAKE", "COMP", "CRV", "SNX", "MKR",
            # Additional DeFi tokens
            "1INCH", "BAL", "YFI", "DYDX", "GRT", "LDO", "FXS", "LQTY", "PERP",
            "REN", "RPL", "ALPHA", "BADGER", "RUNE", "SPELL", "CVX", "INJ", "DODO", "QUICK"
        ],
        "gaming": ["AXS", "SAND", "MANA"],
        "layer2": ["MATIC", "OP", "ARB"],
    }

    if category in categories:
        return categories[category]

    # Jika kategori tidak ditemukan, kembalikan semua token
    return all_tokens

def parse_arguments():
    """
    Parse argumen command line.

    Returns:
        Argumen yang diparsing
    """
    parser = argparse.ArgumentParser(description="Program Arbitrase Cryptocurrency")

    parser.add_argument(
        "--scenario",
        type=int,
        choices=[1, 2, 3],
        help="Skenario arbitrase yang akan dipindai (1: DEX-CEX, 2: DEX-DEX Sama Jaringan, 3: DEX-DEX Beda Jaringan)"
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Jalankan pemindaian secara terus-menerus"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval pemindaian dalam detik (untuk mode continuous)"
    )

    parser.add_argument(
        "--tokens",
        type=str,
        help="Daftar token yang akan dipindai (dipisahkan koma)"
    )

    parser.add_argument(
        "--category",
        type=str,
        choices=["wrapped", "stablecoins", "defi", "gaming", "layer2", "all"],
        help="Kategori token yang akan dipindai (wrapped, stablecoins, defi, gaming, layer2, all)"
    )

    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Jumlah token teratas yang akan dipindai (berdasarkan kapitalisasi pasar)"
    )

    parser.add_argument(
        "--min-profit",
        type=float,
        help="Persentase keuntungan minimum"
    )

    parser.add_argument(
        "--min-liquidity",
        type=float,
        default=10000,
        help="Likuiditas minimum dalam USD"
    )

    return parser.parse_args()

def run_scan(args):
    """
    Menjalankan pemindaian arbitrase.

    Args:
        args: Argumen command line

    Returns:
        Hasil pemindaian
    """
    # Set persentase keuntungan minimum jika diberikan
    if args.min_profit is not None:
        arbitrage_scanner.min_profit_percentage = args.min_profit
        logger.info(f"Persentase keuntungan minimum diatur ke {args.min_profit}%")

    # Parse daftar token jika diberikan
    tokens_to_check = None

    # Jika kategori diberikan, ambil token berdasarkan kategori
    if args.category:
        tokens_to_check = get_tokens_by_category(args.category)
        logger.info(f"Memindai kategori {args.category} dengan {len(tokens_to_check)} token")
    # Jika daftar token diberikan, gunakan daftar tersebut
    elif args.tokens:
        tokens_to_check = [token.strip().upper() for token in args.tokens.split(",")]
        logger.info(f"Memindai token: {', '.join(tokens_to_check)}")

    # Set likuiditas minimum
    if args.min_liquidity is not None:
        # Tambahkan atribut min_liquidity ke arbitrage_scanner jika belum ada
        if not hasattr(arbitrage_scanner, "min_liquidity"):
            arbitrage_scanner.min_liquidity = args.min_liquidity
        else:
            arbitrage_scanner.min_liquidity = args.min_liquidity
        logger.info(f"Likuiditas minimum diatur ke ${args.min_liquidity:,.2f}")

    # Jalankan pemindaian berdasarkan skenario
    if args.scenario == 1:
        logger.info("Menjalankan pemindaian untuk Skenario 1 (DEX-CEX, Sama Jaringan)")
        results = {1: arbitrage_scanner.scan_scenario_1()}
    elif args.scenario == 2:
        logger.info("Menjalankan pemindaian untuk Skenario 2 (DEX-DEX, Sama Jaringan)")
        results = {2: arbitrage_scanner.scan_scenario_2(tokens_to_check)}
    elif args.scenario == 3:
        logger.info("Menjalankan pemindaian untuk Skenario 3 (DEX-DEX, Beda Jaringan)")
        results = {3: arbitrage_scanner.scan_scenario_3(tokens_to_check)}
    else:
        logger.info("Menjalankan pemindaian untuk semua skenario")
        results = arbitrage_scanner.scan_all_scenarios()

    return results

def main():
    """
    Fungsi utama program.
    """
    # Parse argumen
    args = parse_arguments()

    try:
        if args.continuous:
            logger.info(f"Memulai pemindaian terus-menerus dengan interval {args.interval} detik")

            while True:
                try:
                    # Jalankan pemindaian
                    results = run_scan(args)

                    # Tampilkan hasil
                    display_results(results)

                    # Tunggu interval
                    logger.info(f"Menunggu {args.interval} detik sebelum pemindaian berikutnya...")
                    time.sleep(args.interval)

                except KeyboardInterrupt:
                    logger.info("Pemindaian dihentikan oleh pengguna")
                    break

                except Exception as e:
                    logger.error(f"Error saat menjalankan pemindaian: {str(e)}")
                    logger.info("Mencoba lagi dalam 10 detik...")
                    time.sleep(10)

        else:
            # Jalankan pemindaian sekali
            results = run_scan(args)

            # Tampilkan hasil
            display_results(results)

    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")

    except Exception as e:
        logger.error(f"Error tidak terduga: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
