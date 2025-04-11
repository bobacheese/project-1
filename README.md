# Crypto Arbitrage Scanner

Program Python untuk mencari peluang arbitrase cryptocurrency di antara bursa terpusat (CEX) dan terdesentralisasi (DEX) serta antar DEX dalam jaringan yang sama dan berbeda.

## Fitur

Program ini dapat mencari peluang arbitrase dalam tiga skenario:

1. **Skenario 1 (DEX - CEX, Sama Jaringan)**: Mencari perbedaan harga antara DEX dan CEX untuk token yang sama.
2. **Skenario 2 (DEX - DEX, Sama Jaringan)**: Mencari perbedaan harga antara berbagai DEX dalam jaringan yang sama.
3. **Skenario 3 (DEX - DEX, Beda Jaringan)**: Mencari perbedaan harga antara DEX di jaringan yang berbeda untuk token multichain.

Fitur tambahan:
- Dukungan untuk 28 token DeFi populer
- Format output WhatsApp yang mudah dibaca
- Instruksi perdagangan terperinci untuk setiap peluang arbitrase
- Simulasi investasi dalam Rupiah Indonesia dengan perhitungan keuntungan
- Link verifikasi untuk memudahkan validasi peluang

## Instalasi

1. Clone repository ini:
   ```
   git clone https://github.com/username/crypto-arbitrage-scanner.git
   cd crypto-arbitrage-scanner
   ```

2. Buat virtual environment (opsional tapi direkomendasikan):
   ```
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/Mac
   venv\Scripts\activate     # Untuk Windows
   ```

3. Install dependensi:
   ```
   pip install -r requirements.txt
   ```

4. Konfigurasi:
   - Edit file `config.py` untuk menyesuaikan parameter seperti daftar token, CEX, DEX, dan ambang batas keuntungan.

## Penggunaan

### Menjalankan Program

Untuk menjalankan program dengan semua skenario:

```
python main.py
```

### Opsi Command Line

Program ini mendukung beberapa opsi command line:

- `--scenario`: Menentukan skenario yang akan dipindai (1, 2, atau 3)
- `--continuous`: Menjalankan pemindaian secara terus-menerus
- `--interval`: Interval pemindaian dalam detik (untuk mode continuous)
- `--category`: Kategori token yang akan dipindai (defi, stablecoins, gaming, layer2, wrapped, all)
- `--tokens`: Daftar token yang akan dipindai (dipisahkan koma)
- `--min-profit`: Persentase keuntungan minimum
- `--min-liquidity`: Likuiditas minimum dalam USD

Contoh:

```
# Menjalankan pemindaian untuk Skenario 1
python main.py --scenario 1

# Menjalankan pemindaian terus-menerus dengan interval 120 detik
python main.py --continuous --interval 120

# Memindai token tertentu dengan keuntungan minimum 1%
python main.py --tokens WETH,WBTC,LINK --min-profit 1.0

# Memindai kategori DeFi dengan keuntungan minimum 0.5% dan likuiditas minimum $10,000
python main.py --scenario 2 --category defi --min-profit 0.5 --min-liquidity 10000
```

## Output

Program akan menampilkan hasil pemindaian dalam format tabel yang mudah dibaca menggunakan modul `rich`. Hasil juga akan disimpan dalam dua file:

- `arbitrage_opportunities.json`: Data peluang arbitrase lengkap dalam format JSON
- `arbitrage_whatsapp.txt`: Format yang dioptimalkan untuk WhatsApp dengan instruksi perdagangan

## Kategori Token

- **DeFi**: LINK, UNI, AAVE, SUSHI, CAKE, COMP, CRV, SNX, MKR, 1INCH, BAL, YFI, DYDX, GRT, LDO, FXS, LQTY, PERP, REN, RPL, ALPHA, BADGER, RUNE, SPELL, CVX, INJ, DODO, QUICK
- **Stablecoins**: USDT, USDC, DAI, BUSD, FRAX
- **Gaming**: AXS, SAND, MANA
- **Layer2**: MATIC, OP, ARB
- **Wrapped**: WETH, WBTC, WBNB, WMATIC

## Struktur Program

- `main.py`: Entry point program
- `config.py`: Konfigurasi program
- `arbitrage.py`: Logika arbitrase
- `cex_data.py`: Pengambilan data dari CEX
- `dex_data.py`: Pengambilan data dari DEX
- `output.py`: Fungsi output dan pelaporan
- `utils.py`: Fungsi utilitas

## Catatan Penting

- Program ini hanya untuk tujuan informasi dan edukasi.
- Selalu lakukan riset dan analisis risiko sendiri sebelum melakukan arbitrase nyata.
- Harga dan likuiditas di pasar cryptocurrency dapat berubah dengan cepat.
- Biaya transaksi, slippage, dan faktor lain dapat mempengaruhi profitabilitas arbitrase.

## Lisensi

[MIT License](LICENSE)
