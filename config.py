"""
🔧 Naofumi Telegram Bot - Konfigürasyon Dosyası (Render.com için)
Bu dosya Render.com'da environment variables kullanır.
"""

import os
from dotenv import load_dotenv

# .env dosyasını yükle (varsa)
load_dotenv()

######################################
#        TELEGRAM API BİLGİLERİ      #
######################################

# Environment variables'dan al, yoksa varsayılan değerler kullan
print("🔍 Environment variables kontrol ediliyor...")
print(f"API_ID: {os.getenv('API_ID', 'YOK')}")
print(f"API_HASH: {os.getenv('API_HASH', 'YOK')}")
print(f"BOT_TOKEN: {os.getenv('BOT_TOKEN', 'YOK')}")
print(f"BOT_OWNER_ID: {os.getenv('BOT_OWNER_ID', 'YOK')}")

try:
    API_ID = int(os.getenv('API_ID', '0000000'))
except (ValueError, TypeError):
    API_ID = 0000000

API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

try:
    BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID', '0000000'))
except (ValueError, TypeError):
    BOT_OWNER_ID = 0000000

######################################
#           BOT AYARLARI             #
######################################

# Dosya boyutu sınırları (bytes)
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '2097152000'))  # 2GB
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1024'))

# Klasör yolları
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
TEMP_DIR = os.getenv('TEMP_DIR', 'temp')

# Desteklenen formatlar
SUPPORTED_FORMATS = ['mp4', 'mp3', 'm4a', 'webm', 'mkv', 'avi']

# Video süre sınırı (saniye)
MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', '3600'))  # 1 saat

# Özellik durumları
ENABLE_VIDEO_DOWNLOAD = os.getenv('ENABLE_VIDEO_DOWNLOAD', 'true').lower() == 'true'
ENABLE_GUI_CONTROL = os.getenv('ENABLE_GUI_CONTROL', 'false').lower() == 'true'
ENABLE_SCREENSHOT = os.getenv('ENABLE_SCREENSHOT', 'false').lower() == 'true'
ENABLE_ADMIN_PANEL = os.getenv('ENABLE_ADMIN_PANEL', 'true').lower() == 'true'
ENABLE_AUTO_CONVERT = os.getenv('ENABLE_AUTO_CONVERT', 'true').lower() == 'true'

######################################
#           MESAJLAR                 #
######################################

WELCOME_MESSAGE = """
🤖 **Kosemtra Telegram Bot'a Hoş Geldiniz!** 🤖

🎯 **Özellikler:**
• 📺 YouTube video indirme
• 🎵 MP3/MP4 format desteği
• ⚡ Hızlı indirme modu
• ⌨️ Sanal klavye
• 👑 Admin paneli
• 📊 İstatistikler

🚀 **Kullanım:**
Video linkini gönderin ve format seçin!

💡 **Desteklenen Platformlar:**
• YouTube - Tam destek
• TikTok - Tam destek
• Twitter - Tam destek
• Facebook - Tam destek
• Instagram - Geçici olarak devre dışı

🆘 **Yardım için /help komutunu kullanın.**
"""

HELP_MESSAGE = """
🆘 **Yardım Menüsü** 🆘

**📋 Temel Komutlar:**
• `/start` - Bot'u başlat
• `/help` - Bu yardım menüsü
• `/stats` - Bot istatistikleri

**🎯 Video İndirme:**
• Video linkini gönderin
• Format seçin (MP3/MP4)
• İndirme otomatik başlar

**⚡ Hızlı İndirme:**
• `fast:link` - Hızlı MP3 indirme
• `hızlı:link` - Hızlı MP3 indirme
• `quick:link` - Hızlı MP3 indirme

**⌨️ Sanal Klavye:**
• Tıklamalı klavye
• Checkbox alanı
• Not defteri

**👑 Admin Komutları:**
• `/admin_stats` - Admin istatistikleri
• `/admin_users` - Kullanıcı listesi
• `/admin_settings` - Bot ayarları

**📞 Destek:**
Sorun yaşarsanız admin ile iletişime geçin.
"""

ERROR_MESSAGES = {
    'invalid_url': '❌ Geçersiz URL! Lütfen geçerli bir video linki gönderin.',
    'unsupported_platform': '❌ Desteklenmeyen platform! Sadece YouTube, TikTok, Twitter, Facebook desteklenir.',
    'download_failed': '❌ İndirme başarısız! Lütfen tekrar deneyin.',
    'file_too_large': '❌ Dosya çok büyük! Maksimum 2GB desteklenir.',
    'video_too_long': '❌ Video çok uzun! Maksimum 1 saat desteklenir.',
    'conversion_failed': '❌ Dönüştürme başarısız! Lütfen tekrar deneyin.',
    'permission_denied': '❌ Yetkisiz erişim! Bu komutu kullanma yetkiniz yok.',
    'rate_limited': '❌ Çok fazla istek! Lütfen biraz bekleyin.',
    'network_error': '❌ Ağ hatası! Lütfen internet bağlantınızı kontrol edin.',
    'unknown_error': '❌ Bilinmeyen hata! Lütfen tekrar deneyin.'
}

SUCCESS_MESSAGES = {
    'download_started': '✅ İndirme başladı! Lütfen bekleyin...',
    'download_completed': '✅ İndirme tamamlandı!',
    'conversion_started': '🔄 Dönüştürme başladı! Lütfen bekleyin...',
    'conversion_completed': '✅ Dönüştürme tamamlandı!',
    'file_sent': '📤 Dosya gönderildi!',
    'admin_added': '✅ Admin eklendi!',
    'admin_removed': '✅ Admin kaldırıldı!',
    'settings_updated': '✅ Ayarlar güncellendi!'
}

######################################
#           EMOJİLER                 #
######################################

EMOJIS = {
    'video': '📺',
    'audio': '🎵',
    'download': '⬇️',
    'upload': '⬆️',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '🔄',
    'check': '☑️',
    'cross': '❌',
    'star': '⭐',
    'heart': '❤️',
    'fire': '🔥',
    'rocket': '🚀',
    'robot': '🤖',
    'gear': '⚙️',
    'key': '🔑',
    'lock': '🔒',
    'unlock': '🔓',
    'crown': '👑',
    'shield': '🛡️',
    'magic': '✨',
    'thunder': '⚡',
    'sun': '☀️',
    'moon': '🌙',
    'earth': '🌍',
    'flag': '🏁',
    'trophy': '🏆',
    'medal': '🏅',
    'diamond': '💎',
    'money': '💰',
    'gift': '🎁',
    'party': '🎉',
    'confetti': '🎊',
    'balloon': '🎈',
    'cake': '🎂',
    'pizza': '🍕',
    'hamburger': '🍔',
    'fries': '🍟',
    'coffee': '☕',
    'tea': '🍵',
    'beer': '🍺',
    'wine': '🍷',
    'cocktail': '🍸',
    'tropical': '🍹',
    'popcorn': '🍿',
    'candy': '🍭',
    'lollipop': '🍭',
    'chocolate': '🍫',
    'cookie': '🍪',
    'doughnut': '🍩',
    'ice_cream': '🍦',
    'shaved_ice': '🍧',
    'birthday': '🎂',
    'christmas': '🎄',
    'halloween': '🎃',
    'valentine': '💝',
    'mothers_day': '🌹',
    'fathers_day': '👨',
    'new_year': '🎊',
    'easter': '🐰',
    'thanksgiving': '🦃',
    'independence': '🇺🇸',
    'memorial': '🪖',
    'veterans': '🎖️',
    'labor': '👷',
    'columbus': '🚢',
    'presidents': '👔',
    'martin_luther': '✊',
    'groundhog': '🐹',
    'leap_year': '🐸',
    'april_fools': '🤡',
    'earth_day': '🌍',
    'cinco_mayo': '🌮',
    'flag_day': '🇺🇸',
    'fathers_day': '👨',
    'independence_day': '🇺🇸',
    'labor_day': '👷',
    'columbus_day': '🚢',
    'halloween': '🎃',
    'veterans_day': '🎖️',
    'thanksgiving': '🦃',
    'christmas': '🎄',
    'new_years_eve': '🎊'
}

######################################
#           KALİTE AYARLARI          #
######################################

MP3_QUALITIES = {
    '128': '128kbps',
    '192': '192kbps',
    '256': '256kbps',
    '320': '320kbps'
}

MP4_QUALITIES = {
    '360': '360p',
    '480': '480p',
    '720': '720p',
    '1080': '1080p'
}

DEFAULT_MP3_QUALITY = '192'
DEFAULT_MP4_QUALITY = '480'

######################################
#        KONFİGÜRASYON DOĞRULAMA     #
######################################

def validate_config():
    """
    🔍 Konfigürasyon dosyasını doğrular.
    """
    errors = []
    
    # API bilgilerini kontrol et
    if API_ID == 0000000:
        errors.append("API_ID ayarlanmamış")
    
    if not API_HASH:
        errors.append("API_HASH ayarlanmamış")
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN ayarlanmamış")
    
    if BOT_OWNER_ID == 0000000:
        errors.append("BOT_OWNER_ID ayarlanmamış")
    
    # Hata varsa göster
    if errors:
        print("❌ Konfigürasyon hataları:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Konfigürasyon doğru!")
    return True

# Konfigürasyonu doğrula
if __name__ == "__main__":
    validate_config()