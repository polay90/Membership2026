import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from telegram.constants import ChatAction
from config import BOT_TOKEN, ADMIN_IDS
from handler import (
    start, login, send_otp, verify_otp, show_menu, 
    service_callback, process_service, admin_panel, 
    verify_otp, topup_callback, process_topup,
    my_balance, cancel
)
from database import init_db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states
LOGIN, OTP_VERIFICATION, SERVICE_SELECTION, SERVICE_INPUT, ADMIN_TOPUP, ADMIN_VERIFY = range(6)

def main():
    """Start the bot."""
    init_db()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for login
    login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_otp)],
            OTP_VERIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_otp)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Conversation handler for service
    service_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', show_menu)],
        states={
            SERVICE_SELECTION: [CallbackQueryHandler(service_callback)],
            SERVICE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_service)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Conversation handler for admin
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_panel)],
        states={
            ADMIN_TOPUP: [CallbackQueryHandler(topup_callback)],
            ADMIN_VERIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_topup)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(login_conv_handler)
    application.add_handler(service_conv_handler)
    application.add_handler(admin_conv_handler)
    application.add_handler(CommandHandler('balance', my_balance))
    application.add_handler(CommandHandler('help', lambda u, c: u.message.reply_text(get_help_text())))
    application.add_handler(CallbackQueryHandler(service_callback))
    
    # Run the bot
    application.run_polling()

def get_help_text():
    return """
🤖 <b>Bantuan Bot Pusat Jasa Ketenagakerjaan</b>

<b>Perintah User:</b>
/start - Mulai bot
/login - Login dengan nomor WhatsApp + OTP
/menu - Lihat semua layanan
/balance - Cek saldo Anda
/help - Tampilkan bantuan ini
/cancel - Batal transaksi

<b>Perintah Admin:</b>
/admin - Buka panel admin (verifikasi top-up)

<b>Cara Menggunakan:</b>
1. Gunakan /login untuk login dengan nomor WhatsApp
2. Masukkan OTP yang dikirim
3. Gunakan /menu untuk melihat layanan
4. Pilih layanan dan ikuti instruksi
5. Saldo akan dikurangi setelah transaksi berhasil

<b>Pertanyaan?</b>
Hubungi admin untuk bantuan lebih lanjut.
"""

if __name__ == '__main__':
    main()
