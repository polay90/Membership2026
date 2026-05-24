# 🤖 Bot Telegram Pusat Jasa Ketenagakerjaan

Bot Telegram lengkap untuk layanan Pusat Jasa Ketenagakerjaan dengan sistem autentikasi, manajemen saldo, dan 13 layanan berbeda.

## ✨ Fitur Utama

### 🔐 **Autentikasi**
- Login dengan nomor WhatsApp + OTP 6 digit
- Verifikasi otomatis pengguna
- Session management yang aman

### 💼 **13 Layanan Lengkap**
1. Registrasi Reguler - Rp 2.800.000
2. Registrasi VIP - Rp 6.600.000
3. Registrasi Ternak Request Wilayah - Rp 2.500.000
4. JMO MOD Klaim ALL BYPASS - Rp 450.000
5. RESET AKUN - Rp 300.000
6. GMAIL DAN NOMOR VIRTUAL - Rp 150.000
7. BIOMETRIK UPNORMAL - Rp 490.000
8. BYPASS LASIK - Rp 350.000
9. BYPASS BIOMETRIK - Rp 300.000
10. KLAIM ONE DAY EXPERIENCE - Rp 600.000
11. KLAIM ONE DAY NORMAL - Rp 450.000
12. TUNGGAK IURAN ATAU LUNAS IURAN - Rp 550.000
13. BYPASS NIK LUAR NEGERI - Rp 600.000

### 💰 **Manajemen Saldo**
- ✅ Saldo **TIDAK RESET KE NOL** (persistent di database)
- Top-up saldo dengan bukti transfer QRIS
- Verifikasi admin otomatis
- Riwayat transaksi lengkap
- Setiap transaksi tercatat di database

### 👨‍💼 **Admin Panel**
- Verifikasi top-up pengguna
- Lihat statistik pengguna
- Cari informasi pengguna
- Manajemen saldo pengguna

### 🗄️ **Database SQLite**
- User management (user_id, phone_number, balance)
- Transaction logging (setiap pembelian tercatat)
- Top-up requests (dengan verifikasi admin)
- OTP tracking

## 🚀 Instalasi

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/polay90/Pusat-Jasa-Ketenagakerjaan.git
cd Pusat-Jasa-Ketenagakerjaan

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Untuk Linux/Mac:
source venv/bin/activate

# Untuk Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Konfigurasi

1. **Buat file `.env`** dari `.env.example`:
```bash
cp .env.example .env
```

2. **Edit `.env` dan masukkan:**
```
BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
ADMIN_IDS=123456789,987654321
```

3. **Dapatkan BOT_TOKEN:**
   - Chat dengan [@BotFather](https://t.me/botfather) di Telegram
   - Gunakan perintah `/newbot`
   - Ikuti instruksi dan copy token yang diberikan

4. **Dapatkan ADMIN_IDS:**
   - Bot Anda akan menampilkan user_id saat pertama kali digunakan
   - Atau gunakan bot seperti [@userinfobot](https://t.me/userinfobot)

### Menjalankan Bot

```bash
python main.py
```

Bot akan mulai berjalan dan siap menerima perintah.

## 📱 Cara Menggunakan

### User Commands
```
/start      - Mulai bot
/login      - Login dengan nomor WhatsApp + OTP
/menu       - Lihat semua layanan
/balance    - Cek saldo Anda
/help       - Tampilkan bantuan
/cancel     - Batal transaksi
```

### Admin Commands
```
/admin      - Buka panel admin (verifikasi top-up, statistik)
```

### Flow Penggunaan User

1. **Login**
   ```
   /login
   → Masukkan nomor WhatsApp (62...)
   → Masukkan OTP yang dikirim
   ```

2. **Lihat Layanan**
   ```
   /menu
   → Pilih layanan dari daftar
   → Masukkan data yang diminta
   → Saldo akan berkurang otomatis
   ```

3. **Cek Saldo**
   ```
   /balance
   → Tampilkan saldo terkini
   ```

### Flow Penggunaan Admin

1. **Verifikasi Top-up**
   ```
   /admin
   → Pilih "Verifikasi Top-up"
   → Lihat daftar top-up menunggu
   → Approve atau reject top-up
   ```

## 💾 Database Structure

### Tabel `users`
```
- user_id (INTEGER PRIMARY KEY)
- phone_number (TEXT UNIQUE)
- balance (INTEGER) - TIDAK AKAN RESET KE NOL
- is_verified (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Tabel `transactions`
```
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- service_name (TEXT)
- amount (INTEGER)
- status (TEXT)
- service_data (TEXT)
- created_at (TIMESTAMP)
```

### Tabel `topup_requests`
```
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- amount (INTEGER)
- proof_file_id (TEXT)
- status (TEXT) - pending/approved/rejected
- created_at (TIMESTAMP)
- verified_at (TIMESTAMP)
- verified_by (INTEGER)
```

### Tabel `otp`
```
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- otp_code (TEXT)
- created_at (TIMESTAMP)
- expired_at (TIMESTAMP)
- used (INTEGER)
```

## ⚙️ Konfigurasi Layanan

Edit `config.py` untuk mengubah:
- Harga layanan
- Nama layanan
- Persyaratan layanan
- ID admin

```python
SERVICES = {
    'service_key': {
        'name': 'Nama Layanan',
        'price': 1000000,
        'requirements': ['Req 1', 'Req 2'],
        'id': '1'
    }
}
```

## 🔒 Keamanan

- ✅ Saldo persistent (tidak reset ke nol)
- ✅ OTP dengan expire time
- ✅ Admin verification untuk top-up
- ✅ Transaction logging
- ✅ User authentication
- ✅ Environment variables untuk token sensitif

## 📝 File Penting

- `main.py` - Entry point bot
- `config.py` - Konfigurasi layanan & pesan
- `database.py` - Manajemen database
- `handlers.py` - Handler untuk semua event
- `.env` - Environment variables
- `requirements.txt` - Dependencies Python

## 🐛 Troubleshooting

### Bot tidak merespons
- Pastikan `BOT_TOKEN` benar di `.env`
- Pastikan internet connection aktif
- Check logs untuk error message

### Database error
- Pastikan file `bot_database.db` tidak corrupt
- Hapus dan jalankan bot lagi untuk reinitialize

### OTP tidak diterima
- OTP ditampilkan di log (development mode)
- Pastikan waktu server akurat

## 📞 Dukungan

Untuk bantuan lebih lanjut, silakan hubungi admin.

## 📄 Lisensi

MIT License - Gunakan dengan bebas untuk keperluan komersial maupun personal.

---

**Bot Dibuat Dengan ❤️ untuk Pusat Jasa Ketenagakerjaan**
