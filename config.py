"""
Konfigurasi untuk program arbitrase cryptocurrency.
"""

# Daftar CEX yang akan dipantau
CEX_LIST = {
    "binance": {
        "api_key": "",  # Kosongkan jika tidak diperlukan untuk data publik
        "api_secret": "",  # Kosongkan jika tidak diperlukan untuk data publik
        "base_url": "https://api.binance.com",
        "weight_limit": 1200,  # Batas weight per menit
    },
    # Tambahkan CEX lain jika diperlukan
}

# Daftar DEX yang akan dipantau
DEX_LIST = {
    "uniswap_v3": {
        "network": "ethereum",
        "router_address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    },
    "sushiswap": {
        "network": "ethereum",
        "router_address": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    },
    "pancakeswap": {
        "network": "bsc",
        "router_address": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    },
    "quickswap": {
        "network": "polygon",
        "router_address": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
    },
    # Tambahkan DEX lain jika diperlukan
}

# Jaringan yang didukung
NETWORKS = {
    "ethereum": {
        "rpc_url": "https://eth-mainnet.alchemyapi.io/v2/your-api-key",  # Ganti dengan API key Anda
        "chain_id": 1,
        "explorer": "https://etherscan.io",
        "native_token": "ETH",
        "wrapped_native": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "stable_coins": [
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
        ],
    },
    "bsc": {
        "rpc_url": "https://bsc-dataseed.binance.org/",
        "chain_id": 56,
        "explorer": "https://bscscan.com",
        "native_token": "BNB",
        "wrapped_native": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
        "stable_coins": [
            "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC
            "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",  # DAI
        ],
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "chain_id": 137,
        "explorer": "https://polygonscan.com",
        "native_token": "MATIC",
        "wrapped_native": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",  # WMATIC
        "stable_coins": [
            "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT
            "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC
            "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",  # DAI
        ],
    },
}

# Daftar token yang akan dipantau untuk arbitrase
# Format: "symbol": {"address": {"network": "address"}}
TOKENS_TO_MONITOR = {
    # Wrapped Tokens
    "WETH": {
        "address": {
            "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "bsc": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
            "polygon": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        },
        "decimals": 18,
    },
    "WBTC": {
        "address": {
            "ethereum": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
            "bsc": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
            "polygon": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        },
        "decimals": 8,
    },
    "WBNB": {
        "address": {
            "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
            "ethereum": "0x418D75f65a02b3D53B2418FB8E1fe493759c7605",
            "polygon": "0x5c4b7CCBF908E64F32e12c6650ec0C96d717f03F",
        },
        "decimals": 18,
    },
    "WMATIC": {
        "address": {
            "polygon": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
            "ethereum": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
            "bsc": "0xcc42724c6683b7e57334c4e856f4c9965ed682bd",
        },
        "decimals": 18,
    },

    # Stablecoins
    "USDT": {
        "address": {
            "ethereum": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "bsc": "0x55d398326f99059fF775485246999027B3197955",
            "polygon": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        },
        "decimals": 6,
    },
    "USDC": {
        "address": {
            "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "bsc": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
            "polygon": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        },
        "decimals": 6,
    },
    "DAI": {
        "address": {
            "ethereum": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "bsc": "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",
            "polygon": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        },
        "decimals": 18,
    },
    "BUSD": {
        "address": {
            "bsc": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
            "ethereum": "0x4Fabb145d64652a948d72533023f6E7A623C7C53",
        },
        "decimals": 18,
    },

    # DeFi Tokens
    "LINK": {
        "address": {
            "ethereum": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
            "bsc": "0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD",
            "polygon": "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
        },
        "decimals": 18,
    },
    "UNI": {
        "address": {
            "ethereum": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            "bsc": "0xBf5140A22578168FD562DCcF235E5D43A02ce9B1",
            "polygon": "0xb33EaAd8d922B1083446DC23f610c2567fB5180f",
        },
        "decimals": 18,
    },
    "AAVE": {
        "address": {
            "ethereum": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
            "polygon": "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
            "bsc": "0xfb6115445Bff7b52FeB98650C87f44907E58f802",
        },
        "decimals": 18,
    },
    "SUSHI": {
        "address": {
            "ethereum": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
            "polygon": "0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a",
            "bsc": "0x947950BcC74888a40Ffa2593C5798F11Fc9124C4",
        },
        "decimals": 18,
    },
    "CAKE": {
        "address": {
            "bsc": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
            "ethereum": "0x152649eA73beAb28c5b49B26eb48f7EAD6d4c898",
        },
        "decimals": 18,
    },
    "COMP": {
        "address": {
            "ethereum": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
            "polygon": "0x8505b9d2254A7Ae468c0E9dd10Ccea3A837aef5c",
            "bsc": "0x52CE071Bd9b1C4B00A0b92D298c512478CaD67e8",
        },
        "decimals": 18,
    },
    "CRV": {
        "address": {
            "ethereum": "0xD533a949740bb3306d119CC777fa900bA034cd52",
            "polygon": "0x172370d5Cd63279eFa6d502DAB29171933a610AF",
            "bsc": "0x12B036b13A608248A7D7D72bBf8F0e2a3D3e4adc",
        },
        "decimals": 18,
    },
    "SNX": {
        "address": {
            "ethereum": "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
            "polygon": "0x50B728D8D964fd00C2d0AAD81718b71311feF68a",
            "bsc": "0x9Ac983826058b8a9C7Aa1C9171441191232E8404",
        },
        "decimals": 18,
    },
    "MKR": {
        "address": {
            "ethereum": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
            "polygon": "0x6f7C932e7684666C9fd1d44527765433e01fF61d",
            "bsc": "0x5f0Da599BB2ccCfcf6Fdfd7D81743B6020864350",
        },
        "decimals": 18,
    },

    # Gaming & Metaverse Tokens
    "AXS": {
        "address": {
            "ethereum": "0xBB0E17EF65F82Ab018d8EDd776e8DD940327B28b",
            "bsc": "0x715D400F88C167884bbCc41C5FeA407ed4D2f8A0",
        },
        "decimals": 18,
    },
    "SAND": {
        "address": {
            "ethereum": "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",
            "polygon": "0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683",
            "bsc": "0x67b725d7e342d7B611fa85e859Df9697D9378B2e",
        },
        "decimals": 18,
    },
    "MANA": {
        "address": {
            "ethereum": "0x0F5D2fB29fb7d3CFeE444a200298f468908cC942",
            "polygon": "0xA1c57f48F0Deb89f569dFbE6E2B7f46D33606fD4",
        },
        "decimals": 18,
    },

    # Layer 2 & Scaling Tokens
    "MATIC": {
        "address": {
            "ethereum": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
            "bsc": "0xCC42724C6683B7E57334c4E856f4c9965ED682bD",
        },
        "decimals": 18,
    },
    "OP": {
        "address": {
            "ethereum": "0x4200000000000000000000000000000000000042",
            "polygon": "0xC5e00D3b04563950941f7137B5AfA3a534F0D6d6",
        },
        "decimals": 18,
    },
    "ARB": {
        "address": {
            "ethereum": "0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1",
            "polygon": "0xf42e2B8bc2aF8B110b65be98dB1321B1ab8D44F5",
        },
        "decimals": 18,
    },

    # Additional DeFi Tokens
    "1INCH": {
        "address": {
            "ethereum": "0x111111111117dC0aa78b770fA6A738034120C302",
            "bsc": "0x111111111117dC0aa78b770fA6A738034120C302",
            "polygon": "0x9c2C5fd7b07E95EE044DDeba0E97a665F142394f",
        },
        "decimals": 18,
    },
    "BAL": {
        "address": {
            "ethereum": "0xba100000625a3754423978a60c9317c58a424e3D",
            "polygon": "0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3",
        },
        "decimals": 18,
    },
    "YFI": {
        "address": {
            "ethereum": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
            "bsc": "0x88f1A5ae2A3BF98AEAF342D26B30a79438c9142e",
            "polygon": "0xDA537104D6A5edd53c6fBba9A898708E465260b6",
        },
        "decimals": 18,
    },
    "DYDX": {
        "address": {
            "ethereum": "0x92D6C1e31e14520e676a687F0a93788B716BEff5",
            "polygon": "0x4Cf89ca06ad997bC732Dc876ed2A7F26a9E7f361",
        },
        "decimals": 18,
    },
    "GRT": {
        "address": {
            "ethereum": "0xc944E90C64B2c07662A292be6244BDf05Cda44a7",
            "polygon": "0x5fe2B58c013d7601147DcdD68C143A77499f5531",
        },
        "decimals": 18,
    },
    "LDO": {
        "address": {
            "ethereum": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
            "polygon": "0xC3C7d422809852031b44ab29EEC9F1EfF2A58756",
        },
        "decimals": 18,
    },
    "FXS": {
        "address": {
            "ethereum": "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0",
            "polygon": "0x1a3acf6D19267E2d3e7f898f42803e90C9219062",
        },
        "decimals": 18,
    },
    "LQTY": {
        "address": {
            "ethereum": "0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D",
        },
        "decimals": 18,
    },
    "PERP": {
        "address": {
            "ethereum": "0xbC396689893D065F41bc2C6EcbeE5e0085233447",
            "polygon": "0x263534a4Fe3cb249dF46810718B7B612a30ebbff",
        },
        "decimals": 18,
    },
    "REN": {
        "address": {
            "ethereum": "0x408e41876cCCDC0F92210600ef50372656052a38",
            "bsc": "0xA402549d0789a8F40cD679E7ddcCdf980a025C19",
            "polygon": "0x19782D3Dc4701cEeeDcD90f0993f0A9126ed89d0",
        },
        "decimals": 18,
    },
    "RPL": {
        "address": {
            "ethereum": "0xD33526068D116cE69F19A9ee46F0bd304F21A51f",
        },
        "decimals": 18,
    },
    "ALPHA": {
        "address": {
            "ethereum": "0xa1faa113cbE53436Df28FF0aEe54275c13B40975",
            "bsc": "0xa1faa113cbE53436Df28FF0aEe54275c13B40975",
            "polygon": "0x3AE490db48d74B1bC626400135d4616377D0109f",
        },
        "decimals": 18,
    },
    "BADGER": {
        "address": {
            "ethereum": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
            "polygon": "0x1FcbE5937B0cc2adf69772D228fA4205aCF4D9b2",
        },
        "decimals": 18,
    },
    "RUNE": {
        "address": {
            "ethereum": "0x3155BA85D5F96b2d030a4966AF206230e46849cb",
            "bsc": "0x3155BA85D5F96b2d030a4966AF206230e46849cb",
        },
        "decimals": 18,
    },
    "SPELL": {
        "address": {
            "ethereum": "0x090185f2135308BaD17527004364eBcC2D37e5F6",
            "polygon": "0xcdB3C70CD25d1a6B3eC0E2232436C0D1B24e43D4",
        },
        "decimals": 18,
    },
    "CVX": {
        "address": {
            "ethereum": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        },
        "decimals": 18,
    },
    "FRAX": {
        "address": {
            "ethereum": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
            "polygon": "0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89",
        },
        "decimals": 18,
    },
    "INJ": {
        "address": {
            "ethereum": "0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30",
            "bsc": "0xa2B726B1145A4773F68593CF171187d8EBe4d495",
        },
        "decimals": 18,
    },
    "DODO": {
        "address": {
            "ethereum": "0x43Dfc4159D86F3A37A5A4B3D4580b888ad7d4DDd",
            "bsc": "0x67ee3Cb086F8a16f34beE3ca72FAD36F7Db929e2",
            "polygon": "0x6B208E08dcA5Bd820F20b5a048c0497E13b12D7A",
        },
        "decimals": 18,
    },
    "QUICK": {
        "address": {
            "polygon": "0xB5C064F955D8e7F38fE0460C556a72987494eE17",
        },
        "decimals": 18,
    },
}

# Konfigurasi DEX Screener API
DEX_SCREENER = {
    "base_url": "https://api.dexscreener.com",
    "rate_limit": 300,  # Permintaan per menit
}

# Parameter arbitrase
ARBITRAGE_CONFIG = {
    "min_profit_percentage": 0.5,  # Persentase keuntungan minimum (0.5%)
    "gas_price_gwei": {
        "ethereum": 30,
        "bsc": 5,
        "polygon": 50,
    },
    "transaction_fees": {
        "binance": {
            "maker": 0.1,  # 0.1%
            "taker": 0.1,  # 0.1%
            "withdrawal": {
                "ETH": 0.005,
                "BNB": 0.0005,
                "MATIC": 0.1,
                "USDT": 1,
                "USDC": 1,
                # Tambahkan token lain jika diperlukan
            },
        },
        # Tambahkan CEX lain jika diperlukan
    },
    "dex_fees": {
        "uniswap_v3": 0.3,  # 0.3%
        "sushiswap": 0.3,  # 0.3%
        "pancakeswap": 0.25,  # 0.25%
        "quickswap": 0.3,  # 0.3%
        # Tambahkan DEX lain jika diperlukan
    },
    "bridge_fees": {
        "ethereum_to_bsc": 0.1,  # Estimasi biaya bridge dalam %
        "ethereum_to_polygon": 0.05,  # Estimasi biaya bridge dalam %
        "bsc_to_ethereum": 0.1,  # Estimasi biaya bridge dalam %
        "bsc_to_polygon": 0.05,  # Estimasi biaya bridge dalam %
        "polygon_to_ethereum": 0.05,  # Estimasi biaya bridge dalam %
        "polygon_to_bsc": 0.05,  # Estimasi biaya bridge dalam %
    },
}

# Konfigurasi output
OUTPUT_CONFIG = {
    "console_output": True,
    "log_file": "arbitrage.log",
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}

# Konfigurasi penanganan kesalahan
ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 1,  # Detik
    "exponential_backoff": True,
}
