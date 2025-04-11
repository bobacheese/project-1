"""
Fungsi utilitas untuk program arbitrase cryptocurrency.
"""

import time
import logging
import requests
from typing import Dict, Any, Optional, Callable, Union, List, Tuple
from decimal import Decimal, getcontext
from functools import wraps
import config

# Set presisi desimal untuk perhitungan yang akurat
getcontext().prec = 28

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.OUTPUT_CONFIG["log_level"]),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.OUTPUT_CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arbitrage")

def retry_on_exception(
    max_retries: int = config.ERROR_HANDLING["max_retries"],
    retry_delay: int = config.ERROR_HANDLING["retry_delay"],
    exponential_backoff: bool = config.ERROR_HANDLING["exponential_backoff"],
    exceptions: tuple = (requests.RequestException,),
) -> Callable:
    """
    Decorator untuk mencoba kembali fungsi jika terjadi exception.
    
    Args:
        max_retries: Jumlah maksimum percobaan ulang
        retry_delay: Waktu tunggu antara percobaan (detik)
        exponential_backoff: Jika True, waktu tunggu akan meningkat secara eksponensial
        exceptions: Tuple exception yang akan ditangani
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = retry_delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Fungsi {func.__name__} gagal setelah {max_retries} percobaan: {str(e)}")
                        raise
                    
                    logger.warning(f"Percobaan {retries}/{max_retries} untuk {func.__name__} gagal: {str(e)}. Mencoba lagi dalam {current_delay} detik.")
                    time.sleep(current_delay)
                    
                    if exponential_backoff:
                        current_delay *= 2
        
        return wrapper
    
    return decorator

def format_price(price: Union[float, Decimal], decimals: int = 8) -> str:
    """
    Format harga dengan jumlah desimal yang tepat.
    
    Args:
        price: Harga yang akan diformat
        decimals: Jumlah desimal
        
    Returns:
        String harga yang diformat
    """
    if isinstance(price, float):
        price = Decimal(str(price))
    
    return f"{price:.{decimals}f}"

def calculate_price_difference_percentage(
    price1: Union[float, Decimal], 
    price2: Union[float, Decimal]
) -> Decimal:
    """
    Menghitung persentase perbedaan harga antara dua harga.
    
    Args:
        price1: Harga pertama
        price2: Harga kedua
        
    Returns:
        Persentase perbedaan
    """
    if isinstance(price1, float):
        price1 = Decimal(str(price1))
    if isinstance(price2, float):
        price2 = Decimal(str(price2))
    
    if price1 == 0:
        return Decimal('0')
    
    return abs((price2 - price1) / price1) * Decimal('100')

def calculate_profit_after_fees(
    buy_price: Union[float, Decimal],
    sell_price: Union[float, Decimal],
    amount: Union[float, Decimal],
    buy_fee_percentage: Union[float, Decimal],
    sell_fee_percentage: Union[float, Decimal],
    gas_cost: Union[float, Decimal] = Decimal('0'),
    other_fees: Union[float, Decimal] = Decimal('0')
) -> Tuple[Decimal, Decimal]:
    """
    Menghitung keuntungan setelah biaya.
    
    Args:
        buy_price: Harga beli
        sell_price: Harga jual
        amount: Jumlah token
        buy_fee_percentage: Persentase biaya beli
        sell_fee_percentage: Persentase biaya jual
        gas_cost: Biaya gas (dalam mata uang dasar)
        other_fees: Biaya lainnya (dalam mata uang dasar)
        
    Returns:
        Tuple (keuntungan bersih, persentase keuntungan)
    """
    # Konversi ke Decimal jika perlu
    if isinstance(buy_price, float):
        buy_price = Decimal(str(buy_price))
    if isinstance(sell_price, float):
        sell_price = Decimal(str(sell_price))
    if isinstance(amount, float):
        amount = Decimal(str(amount))
    if isinstance(buy_fee_percentage, float):
        buy_fee_percentage = Decimal(str(buy_fee_percentage))
    if isinstance(sell_fee_percentage, float):
        sell_fee_percentage = Decimal(str(sell_fee_percentage))
    if isinstance(gas_cost, float):
        gas_cost = Decimal(str(gas_cost))
    if isinstance(other_fees, float):
        other_fees = Decimal(str(other_fees))
    
    # Biaya beli
    buy_cost = buy_price * amount
    buy_fee = buy_cost * (buy_fee_percentage / Decimal('100'))
    
    # Total biaya beli
    total_buy_cost = buy_cost + buy_fee
    
    # Biaya jual
    sell_revenue = sell_price * amount
    sell_fee = sell_revenue * (sell_fee_percentage / Decimal('100'))
    
    # Total pendapatan jual
    total_sell_revenue = sell_revenue - sell_fee
    
    # Keuntungan bersih
    net_profit = total_sell_revenue - total_buy_cost - gas_cost - other_fees
    
    # Persentase keuntungan
    if total_buy_cost == 0:
        profit_percentage = Decimal('0')
    else:
        profit_percentage = (net_profit / total_buy_cost) * Decimal('100')
    
    return net_profit, profit_percentage

def get_current_timestamp() -> int:
    """
    Mendapatkan timestamp saat ini dalam milidetik.
    
    Returns:
        Timestamp dalam milidetik
    """
    return int(time.time() * 1000)

def is_profitable_opportunity(
    profit_percentage: Union[float, Decimal],
    min_profit_percentage: Union[float, Decimal] = config.ARBITRAGE_CONFIG["min_profit_percentage"]
) -> bool:
    """
    Memeriksa apakah peluang arbitrase menguntungkan.
    
    Args:
        profit_percentage: Persentase keuntungan
        min_profit_percentage: Persentase keuntungan minimum
        
    Returns:
        True jika menguntungkan, False jika tidak
    """
    if isinstance(profit_percentage, float):
        profit_percentage = Decimal(str(profit_percentage))
    if isinstance(min_profit_percentage, float):
        min_profit_percentage = Decimal(str(min_profit_percentage))
    
    return profit_percentage >= min_profit_percentage

def get_token_decimals(token_symbol: str, network: str = "ethereum") -> int:
    """
    Mendapatkan jumlah desimal untuk token.
    
    Args:
        token_symbol: Simbol token
        network: Jaringan token
        
    Returns:
        Jumlah desimal
    """
    if token_symbol in config.TOKENS_TO_MONITOR:
        return config.TOKENS_TO_MONITOR[token_symbol]["decimals"]
    
    # Default decimals jika tidak ditemukan
    return 18

def get_token_address(token_symbol: str, network: str = "ethereum") -> Optional[str]:
    """
    Mendapatkan alamat token di jaringan tertentu.
    
    Args:
        token_symbol: Simbol token
        network: Jaringan token
        
    Returns:
        Alamat token atau None jika tidak ditemukan
    """
    if token_symbol in config.TOKENS_TO_MONITOR:
        addresses = config.TOKENS_TO_MONITOR[token_symbol]["address"]
        if network in addresses:
            return addresses[network]
    
    return None

def is_token_multichain(token_symbol: str) -> bool:
    """
    Memeriksa apakah token tersedia di beberapa jaringan.
    
    Args:
        token_symbol: Simbol token
        
    Returns:
        True jika token multichain, False jika tidak
    """
    if token_symbol in config.TOKENS_TO_MONITOR:
        addresses = config.TOKENS_TO_MONITOR[token_symbol]["address"]
        return len(addresses) > 1
    
    return False

def get_networks_for_token(token_symbol: str) -> List[str]:
    """
    Mendapatkan daftar jaringan di mana token tersedia.
    
    Args:
        token_symbol: Simbol token
        
    Returns:
        Daftar jaringan
    """
    if token_symbol in config.TOKENS_TO_MONITOR:
        return list(config.TOKENS_TO_MONITOR[token_symbol]["address"].keys())
    
    return []

def estimate_gas_cost(network: str, gas_limit: int = 200000) -> Decimal:
    """
    Memperkirakan biaya gas untuk transaksi di jaringan tertentu.
    
    Args:
        network: Nama jaringan
        gas_limit: Batas gas untuk transaksi
        
    Returns:
        Perkiraan biaya gas dalam mata uang asli jaringan
    """
    if network in config.ARBITRAGE_CONFIG["gas_price_gwei"]:
        gas_price_gwei = Decimal(str(config.ARBITRAGE_CONFIG["gas_price_gwei"][network]))
        # Konversi dari gwei ke wei (1 gwei = 10^9 wei)
        gas_price_wei = gas_price_gwei * Decimal('1000000000')
        # Biaya gas = gas_limit * gas_price
        gas_cost_wei = Decimal(str(gas_limit)) * gas_price_wei
        # Konversi dari wei ke mata uang asli (1 ETH/BNB/MATIC = 10^18 wei)
        gas_cost = gas_cost_wei / Decimal('1000000000000000000')
        return gas_cost
    
    # Default jika jaringan tidak ditemukan
    return Decimal('0.01')  # Perkiraan default 0.01 ETH/BNB/MATIC

def get_bridge_fee(source_network: str, target_network: str) -> Decimal:
    """
    Mendapatkan biaya bridge antara dua jaringan.
    
    Args:
        source_network: Jaringan sumber
        target_network: Jaringan tujuan
        
    Returns:
        Biaya bridge dalam persentase
    """
    key = f"{source_network}_to_{target_network}"
    if key in config.ARBITRAGE_CONFIG["bridge_fees"]:
        return Decimal(str(config.ARBITRAGE_CONFIG["bridge_fees"][key]))
    
    # Default jika tidak ditemukan
    return Decimal('0.1')  # Default 0.1%
