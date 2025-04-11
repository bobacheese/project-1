"""
Modul untuk output dan pelaporan menggunakan rich.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED
from rich.theme import Theme

logger = logging.getLogger("arbitrage.output")

# Tema kustom untuk output
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "profit": "bold green",
    "loss": "bold red",
    "neutral": "dim white",
    "highlight": "bold cyan",
    "title": "bold blue",
    "subtitle": "italic cyan",
    "header": "bold magenta",
    "timestamp": "dim yellow",
})

# Inisialisasi console
console = Console(theme=custom_theme)

def print_header():
    """
    Mencetak header program.
    """
    console.print("\n")
    console.print(Panel.fit(
        "[title]CRYPTO ARBITRAGE SCANNER[/title]\n"
        "[subtitle]Mencari peluang arbitrase di CEX dan DEX[/subtitle]",
        border_style="blue",
        box=ROUNDED
    ))
    console.print("\n")

def print_scenario_description(scenario: int):
    """
    Mencetak deskripsi skenario.

    Args:
        scenario: Nomor skenario
    """
    if scenario == 1:
        description = "DEX - CEX, Sama Jaringan"
    elif scenario == 2:
        description = "DEX - DEX, Sama Jaringan"
    elif scenario == 3:
        description = "DEX - DEX, Beda Jaringan"
    else:
        description = "Skenario tidak dikenal"

    console.print(f"[header]Skenario {scenario}: {description}[/header]")
    console.print("\n")

def print_opportunities(opportunities: List[Dict[str, Any]], scenario: int):
    """
    Mencetak daftar peluang arbitrase.

    Args:
        opportunities: Daftar peluang arbitrase
        scenario: Nomor skenario
    """
    if not opportunities:
        console.print("[warning]Tidak ada peluang arbitrase yang ditemukan.[/warning]")
        console.print("\n")
        return

    print_scenario_description(scenario)

    # Buat tabel
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        border_style="blue"
    )

    # Tambahkan kolom
    table.add_column("No", style="dim", width=4)
    table.add_column("Token", style="cyan")
    table.add_column("Beli", style="green")
    table.add_column("Jual", style="red")
    table.add_column("Beli ($)", style="green")
    table.add_column("Jual ($)", style="red")
    table.add_column("Diff (%)", style="yellow")
    table.add_column("Profit (%)", style="bold green")

    if scenario == 3:
        table.add_column("Bridge Fee (%)", style="yellow")

    table.add_column("Likuiditas ($)", style="cyan")
    table.add_column("Link Verifikasi", style="blue")

    # Tambahkan baris
    for i, opp in enumerate(opportunities, 1):
        row = [
            str(i),
            opp["token"],
            opp["buy_platform"],
            opp["sell_platform"],
            f"{opp['buy_price']:.6f}",
            f"{opp['sell_price']:.6f}",
            f"{opp['price_diff_percentage']:.2f}",
            f"{opp['profit_percentage']:.2f}",
        ]

        if scenario == 3:
            row.append(f"{opp['bridge_fee_percentage']:.2f}")

        # Tambahkan likuiditas
        if "buy_liquidity" in opp and "sell_liquidity" in opp:
            liquidity = min(opp["buy_liquidity"], opp["sell_liquidity"])
            row.append(f"{liquidity:,.2f}")
        elif "liquidity" in opp:
            row.append(f"{opp['liquidity']:,.2f}")
        else:
            row.append("N/A")

        # Tambahkan link verifikasi
        verification_links = generate_verification_links(opp, scenario)
        row.append(verification_links)

        table.add_row(*row)

    console.print(table)
    console.print("\n")

def generate_verification_links(opportunity: Dict[str, Any], scenario: int) -> str:
    """
    Menghasilkan link untuk verifikasi manual peluang arbitrase.

    Args:
        opportunity: Detail peluang arbitrase
        scenario: Nomor skenario

    Returns:
        String dengan link verifikasi
    """
    token = opportunity["token"]
    links = []

    # Ekstrak informasi platform dan jaringan
    buy_platform_info = opportunity["buy_platform"]
    sell_platform_info = opportunity["sell_platform"]

    # Ekstrak nama platform (tanpa jaringan)
    buy_platform = buy_platform_info.split(" (")[0].lower()
    sell_platform = sell_platform_info.split(" (")[0].lower()

    # Ekstrak jaringan tidak digunakan dalam fungsi ini

    # Dapatkan alamat token jika tersedia
    token_address = opportunity.get("token_address", "")

    # Generate link berdasarkan platform
    if scenario == 1:  # DEX - CEX
        if "binance" in buy_platform or "binance" in sell_platform:
            binance_symbol = f"{token}USDT"
            links.append(f"[link=https://www.binance.com/en/trade/{binance_symbol}]Binance[/link]")

        # Link untuk DEX
        dex_platform = buy_platform if "binance" in sell_platform else sell_platform

        if dex_platform == "uniswap":
            links.append(f"[link=https://app.uniswap.org/#/swap?inputCurrency={token_address}]Uniswap[/link]")
        elif dex_platform == "sushiswap":
            links.append(f"[link=https://app.sushi.com/swap?inputCurrency={token_address}]SushiSwap[/link]")
        elif dex_platform == "pancakeswap":
            links.append(f"[link=https://pancakeswap.finance/swap?inputCurrency={token_address}]PancakeSwap[/link]")
        elif dex_platform == "curve":
            links.append(f"[link=https://curve.fi/]Curve[/link]")
        elif dex_platform == "balancer":
            links.append(f"[link=https://app.balancer.fi/#/]Balancer[/link]")

    elif scenario == 2 or scenario == 3:  # DEX - DEX
        # Link untuk DEX pertama (beli)
        if buy_platform == "uniswap":
            links.append(f"[link=https://app.uniswap.org/#/swap?inputCurrency={token_address}]Uniswap Buy[/link]")
        elif buy_platform == "sushiswap":
            links.append(f"[link=https://app.sushi.com/swap?inputCurrency={token_address}]SushiSwap Buy[/link]")
        elif buy_platform == "pancakeswap":
            links.append(f"[link=https://pancakeswap.finance/swap?inputCurrency={token_address}]PancakeSwap Buy[/link]")
        elif buy_platform == "curve":
            links.append(f"[link=https://curve.fi/]Curve Buy[/link]")
        elif buy_platform == "balancer":
            links.append(f"[link=https://app.balancer.fi/#/]Balancer Buy[/link]")
        else:
            # Jika platform tidak dikenal, gunakan DEX Screener
            links.append(f"[link=https://dexscreener.com/search?q={token}]DEX Screener Buy[/link]")

        # Link untuk DEX kedua (jual)
        if sell_platform == "uniswap":
            links.append(f"[link=https://app.uniswap.org/#/swap?inputCurrency={token_address}]Uniswap Sell[/link]")
        elif sell_platform == "sushiswap":
            links.append(f"[link=https://app.sushi.com/swap?inputCurrency={token_address}]SushiSwap Sell[/link]")
        elif sell_platform == "pancakeswap":
            links.append(f"[link=https://pancakeswap.finance/swap?inputCurrency={token_address}]PancakeSwap Sell[/link]")
        elif sell_platform == "curve":
            links.append(f"[link=https://curve.fi/]Curve Sell[/link]")
        elif sell_platform == "balancer":
            links.append(f"[link=https://app.balancer.fi/#/]Balancer Sell[/link]")
        else:
            # Jika platform tidak dikenal, gunakan DEX Screener
            links.append(f"[link=https://dexscreener.com/search?q={token}]DEX Screener Sell[/link]")

    # Tambahkan link ke DEX Screener untuk semua skenario
    links.append(f"[link=https://dexscreener.com/search?q={token}]DEX Screener[/link]")

    # Tambahkan link ke CoinGecko
    links.append(f"[link=https://www.coingecko.com/en/coins/{token.lower()}]CoinGecko[/link]")

    return " | ".join(links)


def print_opportunity_details(opportunity: Dict[str, Any]):
    """
    Mencetak detail peluang arbitrase.

    Args:
        opportunity: Detail peluang arbitrase
    """
    scenario = opportunity["scenario"]

    console.print(Panel.fit(
        f"[title]DETAIL PELUANG ARBITRASE[/title]\n"
        f"[subtitle]Skenario {scenario}[/subtitle]",
        border_style="blue",
        box=ROUNDED
    ))

    # Buat tabel untuk informasi umum
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        border_style="blue"
    )

    table.add_column("Parameter", style="cyan")
    table.add_column("Nilai", style="yellow")
    table.add_column("Link Verifikasi", style="blue")

    # Generate link verifikasi
    verification_links = generate_verification_links(opportunity, scenario)

    table.add_row("Token", opportunity["token"], verification_links)
    table.add_row("Platform Beli", opportunity["buy_platform"], "")
    table.add_row("Platform Jual", opportunity["sell_platform"], "")
    table.add_row("Harga Beli", f"{opportunity['buy_price']:.6f} USD", "")
    table.add_row("Harga Jual", f"{opportunity['sell_price']:.6f} USD", "")
    table.add_row("Perbedaan Harga", f"{opportunity['price_diff_percentage']:.2f}%", "")

    if scenario == 3:
        table.add_row("Biaya Bridge", f"{opportunity['bridge_fee_percentage']:.2f}%", "")

    table.add_row("Biaya Beli", f"{opportunity['buy_fee_percentage']:.2f}%", "")
    table.add_row("Biaya Jual", f"{opportunity['sell_fee_percentage']:.2f}%", "")
    table.add_row("Biaya Gas", f"{opportunity['gas_cost']:.6f} USD", "")
    table.add_row("Keuntungan Bersih", f"{opportunity['net_profit']:.6f} USD (untuk 1 token)", "")
    table.add_row("Persentase Keuntungan", f"{opportunity['profit_percentage']:.2f}%", "")
    table.add_row("Timestamp", opportunity["timestamp"], "")

    if "network" in opportunity:
        table.add_row("Jaringan", opportunity["network"], "")

    if scenario == 3:
        table.add_row("Jaringan Beli", opportunity["buy_chain"], "")
        table.add_row("Jaringan Jual", opportunity["sell_chain"], "")

    if "token_address" in opportunity:
        token_address = opportunity["token_address"]
        etherscan_link = ""
        # Pastikan network memiliki nilai default jika tidak tersedia
        network = opportunity.get("network", "ethereum")
        network_name = network if network else "ethereum"

        if network_name == "ethereum":
            etherscan_link = f"[link=https://etherscan.io/token/{token_address}]Etherscan[/link]"
        elif network_name == "bsc":
            etherscan_link = f"[link=https://bscscan.com/token/{token_address}]BSCScan[/link]"
        elif network_name == "polygon":
            etherscan_link = f"[link=https://polygonscan.com/token/{token_address}]PolygonScan[/link]"

        table.add_row("Alamat Token", token_address, etherscan_link)

    if "buy_liquidity" in opportunity and "sell_liquidity" in opportunity:
        table.add_row("Likuiditas Beli", f"{opportunity['buy_liquidity']:,.2f} USD", "")
        table.add_row("Likuiditas Jual", f"{opportunity['sell_liquidity']:,.2f} USD", "")
    elif "liquidity" in opportunity:
        table.add_row("Likuiditas", f"{opportunity['liquidity']:,.2f} USD", "")

    console.print(table)
    console.print("\n")

def print_summary(results: Dict[int, List[Dict[str, Any]]]):
    """
    Mencetak ringkasan hasil pemindaian.

    Args:
        results: Dict dengan skenario sebagai key dan daftar peluang sebagai value
    """
    console.print(Panel.fit(
        "[title]RINGKASAN HASIL PEMINDAIAN[/title]",
        border_style="blue",
        box=ROUNDED
    ))

    # Buat tabel
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=ROUNDED,
        border_style="blue"
    )

    table.add_column("Skenario", style="cyan")
    table.add_column("Deskripsi", style="yellow")
    table.add_column("Jumlah Peluang", style="green")
    table.add_column("Profit Tertinggi", style="bold green")

    # Deskripsi skenario
    scenario_descriptions = {
        1: "DEX - CEX, Sama Jaringan",
        2: "DEX - DEX, Sama Jaringan",
        3: "DEX - DEX, Beda Jaringan"
    }

    # Tambahkan baris
    for scenario, opportunities in results.items():
        description = scenario_descriptions.get(scenario, "Skenario tidak dikenal")
        count = len(opportunities)

        if count > 0:
            # Urutkan berdasarkan profit_percentage (descending)
            sorted_opps = sorted(opportunities, key=lambda x: x["profit_percentage"], reverse=True)
            highest_profit = f"{sorted_opps[0]['profit_percentage']:.2f}%"
        else:
            highest_profit = "N/A"

        table.add_row(
            str(scenario),
            description,
            str(count),
            highest_profit
        )

    console.print(table)
    console.print("\n")

    # Cetak timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[timestamp]Pemindaian selesai pada: {timestamp}[/timestamp]")
    console.print("\n")

def save_opportunities_to_file(results: Dict[int, List[Dict[str, Any]]], filename: str = "arbitrage_opportunities.json"):
    """
    Menyimpan peluang arbitrase ke file.

    Args:
        results: Dict dengan skenario sebagai key dan daftar peluang sebagai value
        filename: Nama file
    """
    try:
        # Konversi Decimal ke float untuk JSON serialization
        data = {}

        for scenario, opportunities in results.items():
            data[str(scenario)] = opportunities

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        # Simpan juga format WhatsApp ke file teks
        whatsapp_message = format_whatsapp_message(results)
        whatsapp_filename = "arbitrage_whatsapp.txt"

        with open(whatsapp_filename, "w", encoding="utf-8") as f:
            f.write(whatsapp_message)

        logger.info(f"Peluang arbitrase berhasil disimpan ke {filename}")
        logger.info(f"Format WhatsApp berhasil disimpan ke {whatsapp_filename}")
        console.print(f"[success]Peluang arbitrase berhasil disimpan ke {filename}[/success]")
        console.print(f"[success]Format WhatsApp berhasil disimpan ke {whatsapp_filename}[/success]")

    except Exception as e:
        logger.error(f"Gagal menyimpan peluang arbitrase ke file: {str(e)}")
        console.print(f"[error]Gagal menyimpan peluang arbitrase ke file: {str(e)}[/error]")

def add_validation_warning():
    """
    Menambahkan peringatan validasi untuk hasil arbitrase.
    """
    console.print(Panel.fit(
        "[warning]⚠️ PERINGATAN VALIDASI ⚠️[/warning]\n\n"
        "Hasil yang ditampilkan mungkin tidak mencerminkan peluang arbitrase yang valid karena:\n"
        "1. Data harga mungkin tidak real-time atau tidak akurat\n"
        "2. Likuiditas yang ditampilkan mungkin tidak mencukupi untuk transaksi yang menguntungkan\n"
        "3. Biaya gas dan slippage belum sepenuhnya diperhitungkan\n"
        "4. Peluang arbitrase biasanya hanya bertahan dalam hitungan detik\n\n"
        "[bold]Selalu verifikasi secara manual sebelum melakukan transaksi nyata![/bold]",
        border_style="yellow",
        box=ROUNDED
    ))
    console.print("\n")

def format_whatsapp_message(results: Dict[int, List[Dict[str, Any]]]) -> str:
    """
    Format hasil pemindaian untuk WhatsApp.

    Args:
        results: Dict dengan skenario sebagai key dan daftar peluang sebagai value

    Returns:
        Pesan yang diformat untuk WhatsApp
    """
    message = "🚀 *CRYPTO ARBITRAGE ALERT* 🚀\n\n"
    message += "⏰ *" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*\n\n"

    # Filter peluang yang tidak realistis
    filtered_results = {}
    for scenario, opportunities in results.items():
        filtered_opps = []
        for opp in opportunities:
            # Filter peluang dengan kriteria yang lebih ketat untuk memastikan validitas
            buy_price = opp.get("buy_price", 1.0)
            sell_price = opp.get("sell_price", 1.0)
            profit_percentage = opp["profit_percentage"]

            # Kriteria filter yang lebih ketat dan realistis untuk stablecoin
            token_name = opp.get("token", "")
            is_stablecoin = token_name.upper() in ["USDT", "USDC", "DAI", "BUSD"]

            # Jika token adalah stablecoin, gunakan filter khusus
            if is_stablecoin:
                # Untuk stablecoin, harga seharusnya mendekati $1
                # Hanya terima peluang jika harga beli > 0.95 dan harga jual < 1.05
                valid_stablecoin = (buy_price > 0.95 and sell_price < 1.05 and
                                  # Profit untuk stablecoin biasanya kecil (0.5% - 3%)
                                  0.5 <= profit_percentage <= 3.0 and
                                  # Pastikan likuiditas sangat tinggi untuk stablecoin
                                  (opp.get("liquidity", 0) > 100000 or
                                   (opp.get("buy_liquidity", 0) > 100000 and opp.get("sell_liquidity", 0) > 100000)) and
                                  # Pastikan token memiliki alamat yang valid
                                  opp.get("token_address", "") != "" and
                                  # Pastikan platform beli dan jual dikenal
                                  opp.get("buy_platform", "") != "unknown" and
                                  opp.get("sell_platform", "") != "unknown")

                if valid_stablecoin:
                    # Tambahkan flag untuk menandai ini peluang stablecoin terverifikasi
                    opp["verified_stablecoin"] = True
                    valid_opportunity = True
                else:
                    valid_opportunity = False
            else:
                # Untuk token non-stablecoin
                valid_opportunity = (
                    # Profit harus realistis (antara 0.5% dan 15%)
                    0.5 <= profit_percentage <= 15.0 and
                    # Harga beli harus cukup signifikan untuk menghindari token sampah
                    buy_price > 0.01 and
                    # Pastikan rasio harga jual/beli tidak terlalu ekstrim (max 20% perbedaan)
                    (sell_price / buy_price) < 1.2 and
                    # Pastikan likuiditas cukup untuk transaksi yang menguntungkan
                    (opp.get("liquidity", 0) > 50000 or
                     (opp.get("buy_liquidity", 0) > 50000 and opp.get("sell_liquidity", 0) > 50000)) and
                    # Pastikan token memiliki alamat yang valid
                    opp.get("token_address", "") != "" and
                    # Pastikan platform beli dan jual dikenal
                    opp.get("buy_platform", "") != "unknown" and
                    opp.get("sell_platform", "") != "unknown")

            if valid_opportunity:
                filtered_opps.append(opp)
        filtered_results[scenario] = filtered_opps

    # Tambahkan ringkasan
    total_opportunities_original = sum(len(opps) for opps in results.values())
    total_opportunities_filtered = sum(len(opps) for opps in filtered_results.values())
    message += f"📊 *Ringkasan:* {total_opportunities_filtered} peluang arbitrase valid ditemukan dari total {total_opportunities_original}\n\n"

    # Tambahkan top 5 peluang dari semua skenario
    all_opportunities = []
    for scenario, opportunities in filtered_results.items():
        for opp in opportunities:
            opp["scenario_num"] = scenario
            all_opportunities.append(opp)

    # Urutkan berdasarkan profit_percentage (descending)
    all_opportunities.sort(key=lambda x: x["profit_percentage"], reverse=True)

    # Ambil top 5
    top_opportunities = all_opportunities[:5]

    if top_opportunities:
        message += "🔥 *TOP 5 PELUANG ARBITRASE* 🔥\n\n"

        for i, opp in enumerate(top_opportunities, 1):
            scenario = opp["scenario_num"]
            token = opp["token"]
            buy_platform = opp["buy_platform"]
            sell_platform = opp["sell_platform"]
            buy_price = opp["buy_price"]
            sell_price = opp["sell_price"]
            profit_percentage = opp["profit_percentage"]

            # Tambahkan emoji berdasarkan profit dan status verifikasi
            if opp.get("verified_stablecoin", False):
                emoji = "💰 ✅ *TERVERIFIKASI*"
            elif profit_percentage > 5.0:
                emoji = "💰💰💰 ⚠️ *VERIFIKASI DIPERLUKAN*"
            elif profit_percentage > 2.0:
                emoji = "💰💰 ⚠️ *VERIFIKASI DIPERLUKAN*"
            elif profit_percentage > 1.0:
                emoji = "💰 ⚠️ *VERIFIKASI DIPERLUKAN*"
            else:
                emoji = "💸 ⚠️ *VERIFIKASI DIPERLUKAN*"

            # Hitung simulasi keuntungan dalam Rupiah
            is_stablecoin = token.upper() in ["USDT", "USDC", "DAI", "BUSD"]
            usd_to_idr_rate = 15500  # Kurs USD ke IDR

            if is_stablecoin:
                modal_optimal_idr = 5000000  # Rp 5 juta untuk stablecoin
                modal_optimal_usd = modal_optimal_idr / usd_to_idr_rate
            else:
                modal_optimal_idr = 10000000  # Rp 10 juta untuk token lainnya
                modal_optimal_usd = modal_optimal_idr / usd_to_idr_rate

            # Hitung jumlah token yang bisa dibeli
            token_amount = modal_optimal_usd / buy_price if buy_price > 0 else 0

            # Hitung nilai jual kotor
            sell_value_usd = token_amount * sell_price

            # Hitung biaya gas dan fee
            # Pastikan network memiliki nilai default jika tidak tersedia
            network = opp.get("network", "ethereum")
            network_name = network if network else "ethereum"
            if network_name == "ethereum":
                gas_fee_usd = 10  # $10 untuk Ethereum
            else:  # BSC atau Polygon
                gas_fee_usd = 0.2  # $0.2 untuk BSC/Polygon

            # Trading fee (0.3% untuk setiap transaksi)
            trading_fee_buy = modal_optimal_usd * 0.003
            trading_fee_sell = sell_value_usd * 0.003

            # Slippage (0.5% untuk setiap transaksi)
            slippage_buy = modal_optimal_usd * 0.005
            slippage_sell = sell_value_usd * 0.005

            # Total biaya
            total_fee_usd = gas_fee_usd + trading_fee_buy + trading_fee_sell + slippage_buy + slippage_sell

            # Keuntungan bersih
            profit_gross_usd = sell_value_usd - modal_optimal_usd
            profit_net_usd = profit_gross_usd - total_fee_usd
            profit_net_idr = profit_net_usd * usd_to_idr_rate

            # Format untuk output
            modal_optimal_idr_str = f"Rp {modal_optimal_idr:,.0f}"
            profit_gross_idr_str = f"Rp {profit_gross_usd * usd_to_idr_rate:,.0f}"
            total_fee_idr_str = f"Rp {total_fee_usd * usd_to_idr_rate:,.0f}"
            profit_net_idr_str = f"Rp {profit_net_idr:,.0f}"

            # Format pesan untuk setiap peluang
            message += f"*{i}. {token}* {emoji}\n"
            message += f"   Skenario: {scenario}\n"
            message += f"   Beli: {buy_platform} (${buy_price:.6f})\n"
            message += f"   Jual: {sell_platform} (${sell_price:.6f})\n"
            message += f"   *Profit: {profit_percentage:.2f}%*\n"

            # Tambahkan simulasi keuntungan
            message += f"   💵 *Simulasi ({modal_optimal_idr_str}):*\n"
            message += f"      Keuntungan Kotor: {profit_gross_idr_str}\n"
            message += f"      Total Biaya: {total_fee_idr_str}\n"
            message += f"      Keuntungan Bersih: {profit_net_idr_str}\n"

            # Tambahkan likuiditas
            if "buy_liquidity" in opp and "sell_liquidity" in opp:
                min_liquidity = min(opp["buy_liquidity"], opp["sell_liquidity"])
                message += f"   Likuiditas: ${min_liquidity:,.2f}\n"
            elif "liquidity" in opp:
                message += f"   Likuiditas: ${opp['liquidity']:,.2f}\n"

            # Tambahkan link verifikasi
            if "token_address" in opp:
                # Pastikan network memiliki nilai default jika tidak tersedia
                network = opp.get("network", "ethereum")
                network_name = network if network else "ethereum"
                if network_name == "ethereum":
                    message += f"   Etherscan: https://etherscan.io/token/{opp['token_address']}\n"
                elif network_name == "bsc":
                    message += f"   BSCScan: https://bscscan.com/token/{opp['token_address']}\n"
                elif network_name == "polygon":
                    message += f"   PolygonScan: https://polygonscan.com/token/{opp['token_address']}\n"

            # Tambahkan link DEX Screener
            message += f"   DEX Screener: https://dexscreener.com/search?q={token}\n"

            # Tambahkan link langsung ke DEX untuk BELI dan JUAL
            buy_platform_name = opp["buy_platform"].split(" (")[0].lower()
            sell_platform_name = opp["sell_platform"].split(" (")[0].lower()
            # Pastikan network memiliki nilai default jika tidak tersedia
            network = opp.get("network", "ethereum")
            network_name = network if network else "ethereum"
            token_address = opp.get('token_address', '')

            # Link untuk platform pembelian (BELI)
            message += f"   🟢 *BELI di {buy_platform_name.capitalize()}*: "
            if buy_platform_name == "uniswap":
                if network_name == "ethereum":
                    message += f"https://app.uniswap.org/#/swap?inputCurrency=ETH&outputCurrency={token_address}\n"
                elif network_name == "polygon":
                    message += f"https://app.uniswap.org/#/swap?chain=polygon&inputCurrency=MATIC&outputCurrency={token_address}\n"
                else:
                    message += f"https://app.uniswap.org/#/swap\n"
            elif buy_platform_name == "sushiswap":
                message += f"https://www.sushi.com/swap?inputCurrency=ETH&outputCurrency={token_address}\n"
            elif buy_platform_name == "pancakeswap":
                if network_name == "bsc":
                    message += f"https://pancakeswap.finance/swap?inputCurrency=BNB&outputCurrency={token_address}\n"
                else:
                    message += f"https://pancakeswap.finance/swap\n"
            elif buy_platform_name == "quickswap" and network_name == "polygon":
                message += f"https://quickswap.exchange/#/swap?inputCurrency=MATIC&outputCurrency={token_address}\n"
            elif buy_platform_name == "balancer":
                message += f"https://app.balancer.fi/#/trade\n"
            elif buy_platform_name == "curve":
                message += f"https://curve.fi/#/ethereum/swap\n"
            else:
                message += f"https://dexscreener.com/search?q={token}\n"

            # Link untuk platform penjualan (JUAL)
            message += f"   🔴 *JUAL di {sell_platform_name.capitalize()}*: "
            if sell_platform_name == "uniswap":
                if network_name == "ethereum":
                    message += f"https://app.uniswap.org/#/swap?inputCurrency={token_address}&outputCurrency=ETH\n"
                elif network_name == "polygon":
                    message += f"https://app.uniswap.org/#/swap?chain=polygon&inputCurrency={token_address}&outputCurrency=MATIC\n"
                else:
                    message += f"https://app.uniswap.org/#/swap\n"
            elif sell_platform_name == "sushiswap":
                message += f"https://www.sushi.com/swap?inputCurrency={token_address}&outputCurrency=ETH\n"
            elif sell_platform_name == "pancakeswap":
                if network_name == "bsc":
                    message += f"https://pancakeswap.finance/swap?inputCurrency={token_address}&outputCurrency=BNB\n"
                else:
                    message += f"https://pancakeswap.finance/swap\n"
            elif sell_platform_name == "quickswap" and network_name == "polygon":
                message += f"https://quickswap.exchange/#/swap?inputCurrency={token_address}&outputCurrency=MATIC\n"
            elif sell_platform_name == "balancer":
                message += f"https://app.balancer.fi/#/trade\n"
            elif sell_platform_name == "curve":
                message += f"https://curve.fi/#/ethereum/swap\n"
            elif sell_platform_name == "apeswap" and network_name == "bsc":
                message += f"https://apeswap.finance/swap?inputCurrency={token_address}&outputCurrency=BNB\n"
            elif sell_platform_name == "biswap" and network_name == "bsc":
                message += f"https://exchange.biswap.org/#/swap?inputCurrency={token_address}&outputCurrency=BNB\n"
            elif sell_platform_name == "bakeryswap" and network_name == "bsc":
                message += f"https://www.bakeryswap.org/#/swap?inputCurrency={token_address}&outputCurrency=BNB\n"
            elif sell_platform_name == "knightswap" and network_name == "bsc":
                message += f"https://knight.knightswap.financial/#/swap?inputCurrency={token_address}&outputCurrency=BNB\n"
            elif sell_platform_name == "dooar" and network_name == "polygon":
                message += f"https://app.dooar.com/swap?inputCurrency={token_address}&outputCurrency=MATIC\n"
            else:
                # Jika DEX tidak dikenal, berikan link ke DEX Screener dan tambahkan peringatan
                # Pastikan network memiliki nilai default jika tidak tersedia
                network_name = network if network else "ethereum"
                message += f"https://dexscreener.com/{network_name}/{token_address} ⚠️ *Verifikasi manual diperlukan*\n"

            # Tambahkan langkah-langkah detail untuk melakukan arbitrase
            message += "\n   📍 *Langkah-langkah Arbitrase:*\n"
            # Pastikan network memiliki nilai default jika tidak tersedia
            network_name = network if network else "unknown"
            message += f"      1. Siapkan modal {modal_optimal_idr_str} di wallet {network_name.upper()}\n"
            message += f"      2. Buka link BELI di {buy_platform_name.capitalize()}\n"
            message += f"      3. Connect wallet dan swap {modal_optimal_usd:.2f} USD ke {token}\n"
            message += f"      4. Setelah transaksi selesai, buka link JUAL di {sell_platform_name.capitalize()}\n"
            message += f"      5. Connect wallet dan swap {token_amount:.6f} {token} ke USD\n"
            message += f"      6. Profit bersih estimasi: {profit_net_idr_str}\n"

            # Tambahkan tips khusus berdasarkan DEX
            message += "\n   💡 *Tips Khusus:*\n"
            if buy_platform_name == "uniswap" or sell_platform_name == "uniswap":
                message += "      • Set gas ke 'High' di Uniswap untuk eksekusi cepat\n"
                message += "      • Gunakan fitur 'Infinite Approval' untuk transaksi cepat\n"
            elif buy_platform_name == "pancakeswap" or sell_platform_name == "pancakeswap":
                message += "      • Set slippage 1% di PancakeSwap untuk token stablecoin\n"
                message += "      • Gunakan BNB Smart Chain untuk biaya gas rendah\n"
            elif buy_platform_name == "quickswap" or sell_platform_name == "quickswap":
                message += "      • Polygon memiliki gas fee rendah, tapi pastikan ada MATIC untuk gas\n"
                message += "      • QuickSwap memiliki likuiditas tinggi untuk stablecoin\n"

            message += "\n"

    # Tambahkan peringatan dan tips verifikasi
    message += "⚠️ *PERINGATAN & TIPS VERIFIKASI* ⚠️\n"
    message += "1. Selalu verifikasi harga dan likuiditas secara manual sebelum melakukan transaksi\n"
    message += "2. Periksa slippage dan biaya gas untuk memastikan transaksi tetap menguntungkan\n"
    message += "3. Gunakan link BELI dan JUAL untuk memeriksa harga real-time di DEX\n"
    message += "4. Peluang arbitrase biasanya hanya bertahan dalam hitungan detik\n"
    message += "5. Pastikan token memiliki likuiditas yang cukup untuk masuk dan keluar posisi\n"
    message += "6. Untuk DEX yang tidak memiliki link langsung, gunakan DEX Screener untuk verifikasi\n"
    message += "7. Periksa riwayat harga token untuk memastikan bukan manipulasi harga sementara\n"

    # Tambahkan panduan cara beli dan jual di berbagai DEX
    message += "\n💳 *PANDUAN TRANSAKSI DI BERBAGAI DEX* 💳\n"
    message += "*Uniswap (Ethereum/Polygon):*\n"
    message += "- Beli: Connect wallet → Pilih token → Input jumlah → Set slippage (0.5-1%) → Swap\n"
    message += "- Jual: Connect wallet → Pilih token → Reverse pair → Set slippage → Swap\n"
    message += "- Gas fee: ~$5-20 (Ethereum), ~$0.01-0.1 (Polygon)\n\n"

    message += "*PancakeSwap (BSC):*\n"
    message += "- Beli: Connect wallet → Pilih token → Input jumlah → Set slippage (0.5-1%) → Swap\n"
    message += "- Jual: Connect wallet → Pilih token → Reverse pair → Set slippage → Swap\n"
    message += "- Gas fee: ~$0.10-0.30\n\n"

    message += "*SushiSwap (Multi-chain):*\n"
    message += "- Beli: Connect wallet → Pilih token → Input jumlah → Set slippage (0.5-1%) → Swap\n"
    message += "- Jual: Connect wallet → Pilih token → Reverse pair → Set slippage → Swap\n"
    message += "- Gas fee: Bervariasi berdasarkan chain\n\n"

    message += "*QuickSwap (Polygon):*\n"
    message += "- Beli: Connect wallet → Pilih token → Input jumlah → Set slippage (0.5-1%) → Swap\n"
    message += "- Jual: Connect wallet → Pilih token → Reverse pair → Set slippage → Swap\n"
    message += "- Gas fee: ~$0.01-0.1\n\n"

    message += "*Curve (Ethereum):*\n"
    message += "- Beli: Connect wallet → Pilih pool → Input jumlah → Set slippage → Swap\n"
    message += "- Jual: Connect wallet → Pilih pool → Reverse pair → Set slippage → Swap\n"
    message += "- Gas fee: ~$5-20\n\n"

    # Tambahkan simulasi modal dan keuntungan
    message += "\n💰 *SIMULASI MODAL & KEUNTUNGAN* 💰\n"
    message += "*Modal Optimal:*\n"
    message += "- Rp 5.000.000 (untuk arbitrase stablecoin)\n"
    message += "- Rp 10.000.000 (untuk arbitrase token lainnya)\n\n"

    message += "*Estimasi Keuntungan per Transaksi:*\n"
    message += "- Stablecoin: 0.5-3% (Rp 25.000 - Rp 150.000)\n"
    message += "- Token lainnya: 1-15% (Rp 100.000 - Rp 1.500.000)\n\n"

    message += "*Biaya yang Perlu Diperhitungkan:*\n"
    message += "- Gas fee: Rp 75.000 - Rp 300.000 (Ethereum), Rp 1.500 - Rp 4.500 (BSC/Polygon)\n"
    message += "- Slippage: 0.5-1% dari nilai transaksi (Rp 25.000 - Rp 100.000)\n"
    message += "- Trading fee: 0.3-1% dari nilai transaksi (Rp 15.000 - Rp 100.000)\n\n"

    message += "*Keuntungan Bersih Estimasi:*\n"
    message += "- Stablecoin: Rp 0 - Rp 50.000 per transaksi (setelah fee)\n"
    message += "- Token lainnya: Rp 50.000 - Rp 1.000.000 per transaksi (setelah fee)\n"

    return message

def print_whatsapp_format(results: Dict[int, List[Dict[str, Any]]]):
    """
    Mencetak hasil pemindaian dalam format WhatsApp.

    Args:
        results: Dict dengan skenario sebagai key dan daftar peluang sebagai value
    """
    message = format_whatsapp_message(results)

    # Cetak pesan dengan format yang menarik
    console.print(Panel.fit(
        message,
        title="[bold green]Format Pesan WhatsApp[/bold green]",
        border_style="green",
        box=ROUNDED
    ))
    console.print("\n")

def display_results(results: Dict[int, List[Dict[str, Any]]]):
    """
    Menampilkan hasil pemindaian.

    Args:
        results: Dict dengan skenario sebagai key dan daftar peluang sebagai value
    """
    print_header()

    # Tambahkan peringatan validasi
    add_validation_warning()

    # Cetak format WhatsApp
    print_whatsapp_format(results)

    # Simpan ke file jika diperlukan
    save_opportunities_to_file(results)
