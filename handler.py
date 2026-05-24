import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction
from config import SERVICES, ADMIN_IDS, OTP_VALIDITY, SERVICES_LIST
from database import (
    get_user, get_user_by_phone, create_user, get_balance, reduce_balance,
    save_transaction, save_otp, verify_otp_code, create_topup_request,
    get_pending_topups, approve_topup, reject_topup, add_balance
)

logger = logging.getLogger(__name__)

# States
LOGIN, OTP_VERIFICATION, SERVICE_SELECTION, SERVICE_INPUT, ADMIN_TOPUP, ADMIN_VERIFY = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command"""
    user_id = update.effective_user.id
    
    # Check if user exists
    user = get_user(user_id)
    
    if user:
        await update.message.reply_text(
            f"👋 Selamat datang kembali!\n\n"
            f"Gunakan /menu untuk melihat layanan atau /balance untuk cek saldo Anda.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"👋 Selamat datang di <b>Pusat Jasa Ketenagakerjaan</b>\n\n"
            f"Silakan gunakan /login untuk masuk dengan nomor WhatsApp Anda.",
            parse_mode='HTML'
        )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Login with phone number"""
    await update.message.reply_text(
        "📱 <b>LOGIN</b>\n\n"
        "Masukkan nomor WhatsApp Anda:\n"
        "Contoh: 6281234567890",
        parse_mode='HTML'
    )
    return LOGIN

async def send_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send OTP code"""
    phone_number = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Validate phone number
    if not phone_number.startswith('62') or len(phone_number) < 10:
        await update.message.reply_text(
            "❌ Nomor WhatsApp tidak valid!\n"
            "Silakan masukkan nomor dengan format: 6281234567890"
        )
        return LOGIN
    
    # Check if user exists, if not create new user
    user = get_user(user_id)
    if not user:
        create_user(user_id, phone_number)
    
    # Generate OTP
    otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expired_at = (datetime.now() + timedelta(seconds=OTP_VALIDITY)).isoformat()
    save_otp(user_id, otp_code, expired_at)
    
    # Store in context for verification
    context.user_data['otp_code'] = otp_code
    context.user_data['phone_number'] = phone_number
    
    logger.info(f"OTP sent to user {user_id}: {otp_code}")
    
    await update.message.reply_text(
        f"✅ OTP telah dikirim ke WhatsApp Anda\n\n"
        f"<b>OTP: {otp_code}</b>\n"
        f"(Kode berlaku 5 menit)\n\n"
        f"Masukkan OTP di bawah ini:",
        parse_mode='HTML'
    )
    return OTP_VERIFICATION

async def verify_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verify OTP code"""
    user_id = update.effective_user.id
    otp_input = update.message.text.strip()
    
    # Simple verification (in production use verify_otp_code from database)
    if otp_input == context.user_data.get('otp_code'):
        await update.message.reply_text(
            "✅ <b>Login berhasil!</b>\n\n"
            "Gunakan /menu untuk melihat layanan.",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ OTP salah!\n"
            "Silakan coba lagi."
        )
        return OTP_VERIFICATION

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show services menu"""
    user_id = update.effective_user.id
    
    # Check if user logged in
    user = get_user(user_id)
    if not user:
        await update.message.reply_text(
            "❌ Anda belum login!\n"
            "Gunakan /login terlebih dahulu."
        )
        return ConversationHandler.END
    
    # Get balance
    balance = get_balance(user_id)
    
    # Create buttons
    keyboard = []
    for i, service in enumerate(SERVICES_LIST):
        button_text = f"{service['name']} - Rp {service['price']:,}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"service_{service['id']}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💼 <b>DAFTAR LAYANAN</b>\n\n"
        f"💰 <b>Saldo Anda:</b> Rp {balance:,}\n\n"
        f"Pilih layanan yang ingin Anda gunakan:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return SERVICE_SELECTION

async def service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle service selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    service_id = query.data.split('_')[1]
    
    # Find service
    service = None
    for svc in SERVICES_LIST:
        if svc['id'] == service_id:
            service = svc
            break
    
    if not service:
        await query.edit_message_text("❌ Layanan tidak ditemukan!")
        return ConversationHandler.END
    
    # Check balance
    balance = get_balance(user_id)
    if balance < service['price']:
        await query.edit_message_text(
            f"❌ <b>Saldo tidak cukup!</b>\n\n"
            f"Layanan: {service['name']}\n"
            f"Biaya: Rp {service['price']:,}\n"
            f"Saldo Anda: Rp {balance:,}\n\n"
            f"Gunakan /topup untuk menambah saldo.",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    # Store service info
    context.user_data['service'] = service
    
    # Show requirements
    if service['requirements']:
        requirements_text = "\n".join([f"• {req}" for req in service['requirements']])
        message = (
            f"📋 <b>{service['name']}</b>\n\n"
            f"💰 <b>Biaya:</b> Rp {service['price']:,}\n\n"
            f"📝 <b>Persyaratan:</b>\n{requirements_text}\n\n"
            f"Silakan masukkan data sesuai persyaratan (pisahkan dengan koma jika lebih dari satu):"
        )
    else:
        message = (
            f"📋 <b>{service['name']}</b>\n\n"
            f"💰 <b>Biaya:</b> Rp {service['price']:,}\n\n"
            f"Konfirmasi untuk melanjutkan (ketik 'YA' atau 'TIDAK'):"
        )
    
    await query.edit_message_text(message, parse_mode='HTML')
    return SERVICE_INPUT

async def process_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process service purchase"""
    user_id = update.effective_user.id
    user_input = update.message.text.strip().upper()
    service = context.user_data.get('service')
    
    if not service:
        await update.message.reply_text("❌ Layanan tidak ditemukan!")
        return ConversationHandler.END
    
    # Check if user confirmed
    if service['requirements'] and user_input not in ['YA', 'TIDAK']:
        # Process requirements
        service_data = user_input
    elif not service['requirements'] and user_input == 'TIDAK':
        await update.message.reply_text("❌ Transaksi dibatalkan.")
        return ConversationHandler.END
    elif not service['requirements'] and user_input == 'YA':
        service_data = 'Confirmed'
    else:
        await update.message.reply_text("❌ Input tidak valid!")
        return SERVICE_INPUT
    
    # Deduct balance
    if reduce_balance(user_id, service['price']):
        # Save transaction
        save_transaction(user_id, service['name'], service['price'], service_data)
        
        # Get new balance
        new_balance = get_balance(user_id)
        
        await update.message.reply_text(
            f"✅ <b>TRANSAKSI BERHASIL!</b>\n\n"
            f"Layanan: {service['name']}\n"
            f"Biaya: Rp {service['price']:,}\n"
            f"Data: {service_data}\n\n"
            f"💰 <b>Saldo Anda sekarang:</b> Rp {new_balance:,}\n\n"
            f"Terima kasih telah menggunakan layanan kami!",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "❌ Transaksi gagal!\n"
            "Saldo tidak cukup atau terjadi kesalahan."
        )
    
    return ConversationHandler.END

async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user balance"""
    user_id = update.effective_user.id
    
    user = get_user(user_id)
    if not user:
        await update.message.reply_text(
            "❌ Anda belum login!\n"
            "Gunakan /login terlebih dahulu."
        )
        return
    
    balance = get_balance(user_id)
    await update.message.reply_text(
        f"💰 <b>SALDO ANDA</b>\n\n"
        f"Rp {balance:,}",
        parse_mode='HTML'
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Admin panel"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Anda bukan admin!")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("✅ Verifikasi Top-up", callback_data="admin_verify")],
        [InlineKeyboardButton("📊 Statistik", callback_data="admin_stats")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👨‍💼 <b>PANEL ADMIN</b>\n\n"
        "Pilih menu admin:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return ADMIN_TOPUP

async def topup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin callbacks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "admin_verify":
        topups = get_pending_topups()
        if not topups:
            await query.edit_message_text("✅ Tidak ada top-up yang menunggu verifikasi.")
            return ConversationHandler.END
        
        message = "📝 <b>TOP-UP MENUNGGU VERIFIKASI</b>\n\n"
        for topup in topups:
            topup_id, user_id, amount, proof_file_id, created_at = topup
            message += f"ID: {topup_id}\nUser: {user_id}\nJumlah: Rp {amount:,}\nWaktu: {created_at}\n\n"
        
        message += "Ketik 'approve [ID]' untuk menyetujui atau 'reject [ID]' untuk menolak."
        await query.edit_message_text(message, parse_mode='HTML')
        return ADMIN_VERIFY
    
    return ConversationHandler.END

async def process_topup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process admin topup action"""
    user_input = update.message.text.strip().lower()
    admin_id = update.effective_user.id
    
    if user_input.startswith('approve '):
        try:
            topup_id = int(user_input.split()[1])
            if approve_topup(topup_id, admin_id):
                await update.message.reply_text(f"✅ Top-up {topup_id} telah disetujui!")
            else:
                await update.message.reply_text(f"❌ Gagal menyetujui top-up {topup_id}")
        except:
            await update.message.reply_text("❌ Format tidak valid! Gunakan: approve [ID]")
    
    elif user_input.startswith('reject '):
        try:
            topup_id = int(user_input.split()[1])
            if reject_topup(topup_id):
                await update.message.reply_text(f"✅ Top-up {topup_id} telah ditolak!")
            else:
                await update.message.reply_text(f"❌ Gagal menolak top-up {topup_id}")
        except:
            await update.message.reply_text("❌ Format tidak valid! Gunakan: reject [ID]")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation"""
    await update.message.reply_text("❌ Operasi dibatalkan.")
    return ConversationHandler.END
