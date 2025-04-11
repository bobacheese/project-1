<div align="center">

# 🚀 Crypto Arbitrage Scanner

<p align="center">
  <img src="https://img.shields.io/badge/by-bobacheese-ff69b4?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/x-artificial_intelligence-00FFFF?style=for-the-badge&logo=openai&logoColor=white">
  <img src="https://img.shields.io/badge/x-vscode-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white">
</p>

```diff
                                     +                  ✨ CRYPTO TRADING ELEVATED ✨                  +
```

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![DeFi](https://img.shields.io/badge/DeFi-Supported-green.svg)]()
[![Networks](https://img.shields.io/badge/Networks-ETH%20|%20BSC%20|%20Polygon-blueviolet.svg)]()


**Temukan peluang arbitrase cryptocurrency secara real-time di berbagai DEX dan CEX**

[Fitur](#fitur) • [Instalasi](#instalasi) • [Penggunaan](#penggunaan) • [Token](#kategori-token) • [Output](#output) • [Catatan](#catatan-penting)

</div>

## 💎 Fitur

Program ini memindai peluang arbitrase cryptocurrency dalam tiga skenario berbeda:

### 🔄 Skenario Arbitrase

1. **DEX ↔️ CEX (Sama Jaringan)** - Memanfaatkan perbedaan harga antara bursa terdesentralisasi dan terpusat
2. **DEX ↔️ DEX (Sama Jaringan)** - Menemukan disparitas harga antar DEX dalam blockchain yang sama
3. **DEX ↔️ DEX (Beda Jaringan)** - Mengidentifikasi peluang arbitrase lintas-rantai untuk token multichain

### ✨ Fitur Unggulan

- 📊 **Analisis Multi-DEX** - Memindai lebih dari 20 DEX populer secara bersamaan
- 🔍 **Deteksi Peluang Real-time** - Menemukan disparitas harga saat terjadi
- 💰 **Simulasi Profit** - Perhitungan keuntungan dalam Rupiah Indonesia dengan estimasi biaya gas
- 📱 **Format WhatsApp** - Output yang dioptimalkan untuk berbagi via WhatsApp
- 🔗 **Link Verifikasi** - Tautan langsung untuk memverifikasi peluang arbitrase
- 🛡️ **Validasi Likuiditas** - Memastikan peluang memiliki likuiditas yang cukup

## 🔧 Instalasi

### Prasyarat

- Python 3.7 atau lebih baru
- Koneksi internet stabil
- Akun di bursa cryptocurrency (opsional, untuk verifikasi)

### Langkah-langkah

```bash
# Clone repository
git clone https://github.com/bobacheese/crypto-arbitrage-scanner.git
cd crypto-arbitrage-scanner

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Untuk Windows:
venv\Scripts\activate
# Untuk macOS/Linux:
# source venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### Konfigurasi

Edit file `config.py` untuk menyesuaikan:
- Daftar token yang dipantau
- Koneksi API ke bursa
- Parameter arbitrase (minimum profit, likuiditas, dll)
- Kurs mata uang untuk simulasi profit

## 💻 Penggunaan

### Perintah Dasar

```bash
# Jalankan dengan pengaturan default
python main.py

# Jalankan skenario spesifik
python main.py --scenario 2 --category defi
```

### 🎛️ Opsi Command Line

| Opsi | Deskripsi | Contoh |
|------|-----------|--------|
| `--scenario` | Skenario arbitrase (1-3) | `--scenario 2` |
| `--category` | Kategori token | `--category defi` |
| `--tokens` | Token spesifik | `--tokens WETH,WBTC` |
| `--min-profit` | Profit minimum (%) | `--min-profit 0.5` |
| `--min-liquidity` | Likuiditas minimum ($) | `--min-liquidity 10000` |
| `--continuous` | Mode pemindaian kontinu | `--continuous` |
| `--interval` | Interval pemindaian (detik) | `--interval 120` |

### 💯 Cara Penggunaan

```bash
# Pemindaian DEX-CEX (Skenario 1)
python main.py --scenario 1

# Pemindaian kontinu setiap 2 menit
python main.py --continuous --interval 120

# Pemindaian token DeFi dengan profit minimum 0.5%
python main.py --scenario 2 --category defi --min-profit 0.5 --min-liquidity 10000

# Pemindaian token spesifik
python main.py --tokens WETH,WBTC,LINK --min-profit 1.0
```

### 📊 Strategi Pemindaian

- **Pemindaian Cepat**: Gunakan `--category` untuk fokus pada kelompok token tertentu
- **Pemindaian Mendalam**: Gunakan mode `--continuous` dengan interval yang lebih panjang
- **Pemindaian Terverifikasi**: Tingkatkan `--min-liquidity` untuk mengurangi risiko slippage

## 📄 Output



### File Output

| File | Deskripsi | Kegunaan |
|------|-----------|----------|
| `arbitrage_opportunities.json` | Data lengkap dalam format JSON | Analisis lanjutan & integrasi dengan tools lain |
| `arbitrage_whatsapp.txt` | Format teks teroptimasi | Berbagi peluang via WhatsApp dengan instruksi perdagangan |

## 🔎 Kategori Token

<div align="center">

### Kategori Token yang Didukung

| Kategori | Tokens | Jumlah |
|----------|--------|--------|
| **💰 DeFi** | LINK, UNI, AAVE, SUSHI, CAKE, COMP, CRV, SNX, MKR, 1INCH, BAL, YFI, DYDX, GRT, LDO, FXS, LQTY, PERP, REN, RPL, ALPHA, BADGER, RUNE, SPELL, CVX, INJ, DODO, QUICK | 28 |
| **💸 Stablecoins** | USDT, USDC, DAI, BUSD, FRAX | 5 |
| **🎮 Gaming** | AXS, SAND, MANA | 3 |
| **🛢️ Layer2** | MATIC, OP, ARB | 3 |
| **💼 Wrapped** | WETH, WBTC, WBNB, WMATIC | 4 |

</div>

### Jaringan yang Didukung

- **Ethereum** - Jaringan utama dengan likuiditas tertinggi
- **Binance Smart Chain (BSC)** - Biaya gas rendah, throughput tinggi
- **Polygon** - Solusi scaling Layer-2 dengan biaya transaksi minimal

## 📚 Struktur Kode

```
crypto-arbitrage-scanner/
├── main.py           # Entry point program
├── config.py         # Konfigurasi & parameter
├── arbitrage.py      # Logika arbitrase utama
├── cex_data.py       # Pengambilan data dari CEX
├── dex_data.py       # Pengambilan data dari DEX
├── output.py         # Formatter output & pelaporan
└── utils.py          # Fungsi utilitas
```

## ⚠️ Catatan Penting

> **Disclaimer**: Program ini hanya untuk tujuan informasi dan edukasi.

- **Risiko Pasar**: Harga dan likuiditas cryptocurrency dapat berubah dalam hitungan detik
- **Biaya Transaksi**: Gas fees, biaya trading, dan slippage dapat mengurangi profitabilitas
- **Due Diligence**: Selalu verifikasi peluang arbitrase sebelum melakukan transaksi nyata
- **Keamanan**: Gunakan wallet terpisah dengan dana terbatas untuk aktivitas arbitrase

## 📝 Kontribusi

Kontribusi sangat diterima! Jika Anda ingin berkontribusi:

1. Fork repositori ini
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## 🔒 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.

## 👨‍💻 Kontak

Bobacheese - [@bobacheese](https://github.com/bobacheese)

Link Proyek: [https://github.com/bobacheese/crypto-arbitrage-scanner](https://github.com/bobacheese/crypto-arbitrage-scanner)

---

<div align="center">

<img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red.svg?style=for-the-badge" alt="Made with love">

**© 2025 bobacheese | Powered by AI | Built with VSCode**

</div>
