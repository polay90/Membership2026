import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8514127937:AAFn2nk2ON0Zkdgi9grjPtib0wP8yGn0sY8')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

# Database
DATABASE_NAME = 'bot_database.db'

# OTP Configuration
OTP_VALIDITY = 300  # 5 minutes in seconds

# Services Configuration
SERVICES = {
    'registrasi_reguler': {
        'name': 'Registrasi Reguler',
        'price': 2800000,
        'requirements': ['NO KTP', 'EMAIL', 'NO WHATSAPP'],
        'id': '1'
    },
    'registrasi_vip': {
        'name': 'Registrasi VIP',
        'price': 6600000,
        'requirements': ['NO KTP', 'EMAIL', 'NO WHATSAPP'],
        'id': '2'
    },
    'registrasi_ternak': {
        'name': 'Registrasi Ternak Request Wilayah',
        'price': 2500000,
        'requirements': ['ID TELEGRAM', 'USERNAME'],
        'id': '3'
    },
    'jmo_mod': {
        'name': 'JMO MOD Klaim ALL BYPASS',
        'price': 450000,
        'requirements': ['ID TELEGRAM', 'USERNAME'],
        'id': '4'
    },
    'reset_akun': {
        'name': 'RESET AKUN',
        'price': 300000,
        'requirements': [],
        'id': '5'
    },
    'gmail_nomor': {
        'name': 'GMAIL DAN NOMOR VIRTUAL',
        'price': 150000,
        'requirements': [],
        'id': '6'
    },
    'biometrik_upnormal': {
        'name': 'BIOMETRIK UPNORMAL',
        'price': 490000,
        'requirements': [],
        'id': '7'
    },
    'bypass_lasik': {
        'name': 'BYPASS LASIK',
        'price': 350000,
        'requirements': [],
        'id': '8'
    },
    'bypass_biometrik': {
        'name': 'BYPASS BIOMETRIK',
        'price': 300000,
        'requirements': [],
        'id': '9'
    },
    'one_day_exp': {
        'name': 'KLAIM ONE DAY EXPERIENCE',
        'price': 600000,
        'requirements': [],
        'id': '10'
    },
    'one_day_normal': {
        'name': 'KLAIM ONE DAY NORMAL',
        'price': 450000,
        'requirements': [],
        'id': '11'
    },
    'tunggak_iuran': {
        'name': 'TUNGGAK IURAN ATAU LUNAS IURAN',
        'price': 550000,
        'requirements': [],
        'id': '12'
    },
    'bypass_nik_ln': {
        'name': 'BYPASS NIK LUAR NEGERI',
        'price': 600000,
        'requirements': [],
        'id': '13'
    },
}

SERVICES_LIST = list(SERVICES.values())
