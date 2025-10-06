#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🤖 Naofumi Telegram Bot - Render.com Version
Bu dosya Render.com'a deploy edilmek üzere özelleştirilmiştir.
"""

######################################
#        GEREKLİ KÜTÜPHANELER        #
######################################
import os
import sys
import locale
import logging
import time
import math
import signal
import asyncio
import requests
import threading
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from file_finder import find_downloaded_file # Dosya bulma modülü

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
# MoviePy import'u kaldırıldı - Render.com'da sorun çıkarıyor
MOVIEPY_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    print("UYARI: tqdm kutuphanesi bulunamadi. Lutfen 'pip install tqdm' ile yukleyin.")
    tqdm = None

try:
    from PIL import Image
except ImportError:
    print("HATA: Pillow kutuphanesi bulunamadi. Lutfen 'pip install Pillow' ile yukleyin.")
    sys.exit(1)

# PyAutoGUI modulu kaldirildi - Render.com'da GUI ortami yok
AUTO_GUI_ENABLED = False

try:
    from admin_panel import admin_panel
    print("Admin Panel modulu yuklendi - Yonetim sistemi aktif.")
    ADMIN_PANEL_ENABLED = True
except ImportError:
    print("UYARI: Admin Panel modulu bulunamadi. Yonetim sistemi devre disi.")
    ADMIN_PANEL_ENABLED = False

try:
    from advanced_features import advanced_features
    print("Gelismis Ozellikler modulu yuklendi - TikTok, Twitter destegi aktif.")
    ADVANCED_FEATURES_ENABLED = True
except ImportError:
    print("UYARI: Gelismis Ozellikler modulu bulunamadi. TikTok, Twitter destegi devre disi.")
    ADVANCED_FEATURES_ENABLED = False

try:
    from virtual_keyboard import virtual_keyboard
    print("Sanal Klavye modulu yuklendi - Tiklamali klavye ozelligi aktif.")
    VIRTUAL_KEYBOARD_ENABLED = True
except ImportError:
    print("UYARI: Sanal Klavye modulu bulunamadi. Tiklamali klavye ozelligi devre disi.")
    VIRTUAL_KEYBOARD_ENABLED = False

######################################
#        KONFİGÜRASYON YÜKLEME       #
######################################

try:
    from config import *
    print("✅ Konfigürasyon dosyası başarıyla yüklendi.")
    
    # Konfigürasyon doğrulaması
    if not validate_config():
        print("❌ Konfigürasyon hataları var. Lütfen config.py dosyasını kontrol edin.")
        sys.exit(1)
        
except ImportError:
    print("❌ config.py dosyası bulunamadı. Lütfen config.py dosyasını oluşturun.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Konfigürasyon yüklenirken hata: {e}")
    sys.exit(1)

# API bilgilerini kontrol et
if API_ID == 0000000 or not API_HASH or not BOT_TOKEN:
    print("❌ Lütfen config.py dosyasında API bilgilerinizi doldurun.")
    print("   - API_ID: Telegram API ID'niz")
    print("   - API_HASH: Telegram API Hash'iniz") 
    print("   - BOT_TOKEN: Bot token'ınız")
    sys.exit(1)

# İndirme klasörlerini oluştur
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

app = Client("kosemtra_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask uygulaması (Render.com için)
web_app = Flask(__name__)

@web_app.route('/health')
def health_check():
    """Health check endpoint for Render.com"""
    current_time = time.time()
    uptime = current_time - bot_stats.get('start_time', current_time)
    
    return jsonify({
        'status': 'healthy',
        'bot_running': True,
        'uptime_seconds': int(uptime),
        'uptime_formatted': str(timedelta(seconds=int(uptime))),
        'total_downloads': bot_stats.get('total_downloads', 0),
        'total_users': len(bot_stats.get('total_users', set())),
        'total_errors': bot_stats.get('total_errors', 0),
        'last_keep_alive': bot_stats.get('last_keep_alive', 0),
        'keep_alive_count': bot_stats.get('keep_alive_count', 0),
        'last_keep_alive_ago': int(current_time - bot_stats.get('last_keep_alive', current_time)),
        'timestamp': current_time,
        'memory_usage': 'N/A',  # Render.com'da psutil kullanımı sınırlı
        'version': '2.0.0'
    })

@web_app.route('/')
def home():
    """Ana sayfa"""
    return jsonify({
        'message': 'Kosemtra Telegram Bot is running!',
        'status': 'active',
        'version': '2.0.0',
        'features': {
            'youtube': True,
            'tiktok': ADVANCED_FEATURES_ENABLED,
            'twitter': ADVANCED_FEATURES_ENABLED,
            'facebook': ADVANCED_FEATURES_ENABLED,
            'instagram': False,  # Geçici olarak devre dışı
            'virtual_keyboard': VIRTUAL_KEYBOARD_ENABLED,
            'admin_panel': ADMIN_PANEL_ENABLED,
            'gui_control': AUTO_GUI_ENABLED
        }
    })

@web_app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint - hızlı yanıt için"""
    try:
        # Webhook verilerini al
        update = request.get_json()
        
        # İşlemi arka planda çalıştır
        threading.Thread(target=handle_webhook_update, args=(update,), daemon=True).start()
        
        # Hemen yanıt dön
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Webhook hatası: {e}")
        return 'ERROR', 500

def handle_webhook_update(update):
    """Webhook güncellemelerini işle"""
    try:
        # Bu fonksiyon Telegram webhook güncellemelerini işler
        # Şu an için basit bir log
        logger.info(f"Webhook güncellemesi alındı: {update}")
        
    except Exception as e:
        logger.error(f"Webhook işleme hatası: {e}")

@web_app.route('/stats')
def stats():
    """Bot istatistikleri"""
    current_time = time.time()
    uptime = current_time - bot_stats.get('start_time', current_time)
    
    return jsonify({
        'bot_stats': {
            'uptime_seconds': int(uptime),
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_downloads': bot_stats.get('total_downloads', 0),
            'total_users': len(bot_stats.get('total_users', set())),
            'total_errors': bot_stats.get('total_errors', 0),
            'keep_alive_count': bot_stats.get('keep_alive_count', 0),
            'last_keep_alive_ago': int(current_time - bot_stats.get('last_keep_alive', current_time))
        },
        'system': {
            'python_version': sys.version,
            'platform': sys.platform,
            'timestamp': current_time
        }
    })

@web_app.route('/test')
def test():
    """Test endpoint - bot durumunu kontrol et"""
    return jsonify({
        'status': 'Bot çalışıyor',
        'message': 'Test başarılı! Bot aktif.',
        'timestamp': time.time(),
        'version': '2.0.0'
    })

# Bot istatistikleri
bot_stats = {
    'start_time': time.time(),
    'total_downloads': 0,
    'total_users': set(),
    'total_errors': 0,
    'last_keep_alive': time.time(),
    'keep_alive_count': 0
}

# Keep-alive sistemi
def keep_alive():
    """Bot'un uykuya geçmesini engellemek için her 10 dakikada bir kendi URL'sine istek gönder"""
    while True:
        try:
            # Bot URL'ini al
            bot_url = os.getenv('RENDER_EXTERNAL_URL', 'https://kosemtra-telegram-bot.onrender.com')
            
            # Health check endpoint'ine istek gönder
            response = requests.get(f"{bot_url}/health", timeout=10)
            
            if response.status_code == 200:
                bot_stats['last_keep_alive'] = time.time()
                bot_stats['keep_alive_count'] += 1
                logger.info(f"✅ Keep-alive başarılı: {response.status_code} - Count: {bot_stats['keep_alive_count']}")
            else:
                logger.warning(f"⚠️ Keep-alive uyarı: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Keep-alive hatası: {e}")
        
        # 10 dakika bekle
        time.sleep(600)

# Keep-alive thread'ini başlat
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()
logger.info("🔄 Keep-alive sistemi başlatıldı")

# URL cache sistemi (callback data boyutu limiti için)
url_cache = {}
url_cache_counter = 0

def cache_url(url: str) -> str:
    """URL'yi cache'e ekle ve kısa ID döndür"""
    global url_cache_counter
    
    # URL'yi hash'le ve kısa ID oluştur
    import hashlib
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    url_id = f"u_{url_hash}"
    
    # Cache'e ekle
    url_cache[url_id] = url
    url_cache_counter += 1
    
    logger.info(f"URL cache'e eklendi: {url_id} -> {url[:50]}...")
    return url_id

def get_cached_url(url_id: str) -> str:
    """Cache'den URL al"""
    url = url_cache.get(url_id, '')
    if url:
        logger.info(f"URL cache'den alındı: {url_id} -> {url[:50]}...")
    else:
        logger.warning(f"URL cache'de bulunamadı: {url_id}")
    return url

######################################
#          FONKSİYONLAR             #
######################################

async def send_file(client, chat_id, video_file, video_title, waiting_message, thumbnail_file=None):
    """
    📤 İndirilen video dosyasını Telegram üzerinden gönderir.
    ⏱️ Video süresi, çözünürlük vb. bilgileri otomatik tespit edilir.
    """
    try:
        start_time = time.time()
        last_update_time = start_time

        duration = 0
        width = 0
        height = 0

        async def progress_callback(current, total):
            nonlocal last_update_time
            elapsed_time = time.time() - start_time
            percent_complete = current / total * 100
            eta = (total - current) / (current / elapsed_time) if current > 0 else 0

            if time.time() - last_update_time >= 5:
                try:
                    await waiting_message.edit_text(
                        f"📤 Video gönderiliyor...\n"
                        f"İlerleme: {percent_complete:.1f}%\n"
                        f"⏱️ ETA: {int(eta)} saniye"
                    )
                    last_update_time = time.time()
                except Exception as e:
                    logger.error(f"İlerleme mesajı güncellenirken hata: {e}")

        # Dosya boyutunu al
        file_size = os.path.getsize(video_file)
        file_size_mb = file_size / (1024 * 1024)
        
        # Thumbnail varsa gönder
        if thumbnail_file and os.path.exists(thumbnail_file):
            try:
                await client.send_photo(
                    chat_id=chat_id,
                    photo=thumbnail_file,
                    caption=f"🎬 **{video_title}**\n\n"
                           f"📁 **Dosya:** {os.path.basename(video_file)}\n"
                           f"📊 **Boyut:** {file_size_mb:.1f} MB"
                )
            except Exception as e:
                logger.error(f"Thumbnail gönderilirken hata: {e}")

        # Video dosyasını gönder
        await client.send_video(
            chat_id=chat_id,
            video=video_file,
            caption=f"🎬 **{video_title}**\n\n"
                   f"📁 **Dosya:** {os.path.basename(video_file)}\n"
                   f"📊 **Boyut:** {file_size_mb:.1f} MB",
            progress=progress_callback
        )

        # İstatistikleri güncelle
        bot_stats['total_downloads'] += 1
        bot_stats['total_users'].add(chat_id)

        # Bekleme mesajını sil
        try:
            await waiting_message.delete()
        except Exception:
            pass

        logger.info(f"Video başarıyla gönderildi: {video_title}")

    except Exception as e:
        logger.error(f"Video gönderilirken hata: {e}")
        try:
            await waiting_message.edit_text(f"❌ Video gönderilemedi: {e}")
        except Exception:
            pass

async def download_video(client, message, url, format_type, quality=None):
    """
    📥 Video indirme fonksiyonu
    """
    try:
        logger.info(f"Video indirme başladı: {url}")
        
        # Platform tespiti
        platform = None
        if ADVANCED_FEATURES_ENABLED:
            platform = advanced_features.detect_platform(url)
        
        # yt-dlp ayarları - YouTube bot koruması bypass (Alternatif yöntem)
        ydl_opts = {
            'outtmpl': '/tmp/%(title)s.%(ext)s',  # Render.com'da /tmp kullan
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'socket_timeout': 120,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'quiet': True,
            # YouTube bot koruması için alternatif ayarlar
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_music', 'android_creator', 'android', 'web'],
                    'comment_sort': ['top'],
                    'max_comments': [0],
                    'include_live_chat': False,
                    'skip_download': False,
                    'age_limit': [0],
                    'geo_bypass': True,
                    'geo_bypass_country': 'US'
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            'sleep_interval': 5,
            'max_sleep_interval': 20,
            'sleep_interval_requests': 5,
            'sleep_interval_subtitles': 5,
            'concurrent_fragment_downloads': 1,
            'throttled_rate': '500K',
            # Alternatif çözümler
            'cookiesfrombrowser': None,
            'cookiefile': None,
            'no_check_certificate': True,
            'prefer_insecure': False,
        }
        
        # Format ayarları
        if format_type == 'mp3':
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality or DEFAULT_MP3_QUALITY,
            }]
        else:  # mp4
            if quality:
                ydl_opts['format'] = f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]/best'
            else:
                ydl_opts['format'] = 'best[ext=mp4]/best'
        
        # Platform emojisi
        platform_emoji = "🎬"
        if ADVANCED_FEATURES_ENABLED and platform:
            platform_emoji = advanced_features.get_platform_emoji(platform)
        
        status_msg = await message.reply_text(f"{platform_emoji} **Video indiriliyor...**\n\nLütfen bekleyin...")
        
        start_time = time.time()
        
        # İlk deneme - normal yt-dlp
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info_dict)
        except Exception as e:
            logger.warning(f"İlk yt-dlp denemesi başarısız: {e}")
            
            # İkinci deneme - farklı ayarlarla
            logger.info("Alternatif yt-dlp ayarları deneniyor...")
            ydl_opts_alt = ydl_opts.copy()
            ydl_opts_alt['extractor_args']['youtube']['player_client'] = ['android', 'web']
            ydl_opts_alt['http_headers']['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
            
            try:
                with YoutubeDL(ydl_opts_alt) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
            except Exception as e2:
                logger.warning(f"İkinci yt-dlp denemesi başarısız: {e2}")
                
                # Üçüncü deneme - minimal ayarlarla
                logger.info("Minimal yt-dlp ayarları deneniyor...")
                ydl_opts_minimal = {
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 60,
                    'retries': 2,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                    }
                }
                
                with YoutubeDL(ydl_opts_minimal) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
            
            # Dosya uzantısını düzelt
            if format_type == 'mp3':
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            else:
                file_name = file_name.rsplit(".", 1)[0] + ".mp4"
            
            # Render.com uyumlu dosya kontrolü - Video indirme
            try:
                file_name = find_downloaded_file(file_name, "Video indirme")
            except Exception as e:
                logger.error(f"Video indirme - Dosya bulunamadı: {e}")
                raise Exception(f"Dosya bulunamadı: {file_name}")
            
            # Dosya boyutu kontrolü
            file_size = os.path.getsize(file_name)
            if file_size > MAX_FILE_SIZE:
                raise Exception(f"Dosya çok büyük! Maksimum {MAX_FILE_SIZE / (1024*1024*1024):.1f}GB desteklenir.")
            
            # Thumbnail indirme
            thumbnail_url = info_dict.get('thumbnail')
            thumbnail_file = None
            if thumbnail_url:
                try:
                    thumbnail_file = f"/tmp/{os.path.basename(file_name)}_thumb.jpg"
                    response = requests.get(thumbnail_url)
                    with open(thumbnail_file, 'wb') as f:
                        f.write(response.content)
                except:
                    thumbnail_file = None
            
            # Dosya boyutu ve süre
            elapsed_time = time.time() - start_time
            file_size_mb = file_size / (1024 * 1024)
            
            await status_msg.edit_text(
                f"✅ **İndirme Tamamlandı!** ✅\n\n"
                f"📁 **Dosya:** {os.path.basename(file_name)}\n"
                f"📊 **Boyut:** {file_size_mb:.1f} MB\n"
                f"⏱️ **Süre:** {int(elapsed_time)} saniye\n"
                f"📤 **Gönderiliyor...**"
            )
            
            # Dosya gönderme
            title = info_dict.get('title', 'Video')
            await send_file(client, message.chat.id, file_name, title, status_msg, thumbnail_file)
            
            # Geçici dosyaları temizle
            try:
                if thumbnail_file and os.path.exists(thumbnail_file):
                    os.remove(thumbnail_file)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Video indirme hatası: {e}", exc_info=True)
        bot_stats['total_errors'] += 1
        
        # Hata türüne göre özel mesaj
        error_msg = str(e).lower()
        if "sign in to confirm" in error_msg or "bot" in error_msg:
            await message.reply_text(
                "❌ **YouTube Bot Koruması Tespit Edildi**\n\n"
                "YouTube geçici olarak bot erişimini engelliyor.\n\n"
                "🔄 **Çözümler:**\n"
                "• Birkaç dakika bekleyip tekrar deneyin\n"
                "• Farklı bir video linki deneyin\n"
                "• Bot yeniden başlatılıyor...\n\n"
                "⏱️ **Tahmini süre:** 5-10 dakika"
            )
        elif "429" in error_msg or "too many requests" in error_msg:
            await message.reply_text(
                "❌ **Çok Fazla İstek**\n\n"
                "YouTube çok fazla istek aldığı için geçici olarak engelliyor.\n\n"
                "🔄 **Çözüm:**\n"
                "• 10-15 dakika bekleyin\n"
                "• Daha sonra tekrar deneyin"
            )
        elif "not found" in error_msg or "unavailable" in error_msg:
            await message.reply_text(
                "❌ **Video Bulunamadı**\n\n"
                "Bu video mevcut değil veya erişim engellenmiş.\n\n"
                "🔄 **Çözüm:**\n"
                "• Video linkinin doğru olduğundan emin olun\n"
                "• Farklı bir video deneyin"
            )
        else:
            await message.reply_text(
                f"❌ **Video İndirme Hatası**\n\n"
                f"**Hata:** {str(e)[:200]}...\n\n"
                f"🔄 **Çözüm:**\n"
                f"• Lütfen tekrar deneyin\n"
                f"• Farklı bir video linki kullanın\n"
                f"• Sorun devam ederse admin ile iletişime geçin"
            )

######################################
#           MESAJ HANDLERS           #
######################################

@app.on_message(filters.command("start"))
async def start(client, message):
    """
    👋 /start komutu ile bot başlatıldığında karşılama mesajı gönderilir.
    """
    # Kullanıcı aktivitesini kaydet
    if ADMIN_PANEL_ENABLED:
        admin_panel.log_user_activity(message.from_user.id, "start_command")
    
    keyboard = [
        [
            InlineKeyboardButton("⚡ Hızlı İndirme", callback_data="fast_download"),
            InlineKeyboardButton("📺 Video İndir", callback_data="quick_download"),
            InlineKeyboardButton("⌨️ Sanal Klavye", callback_data="vk_main_menu")
        ],
        [
            InlineKeyboardButton("☑️ Checkbox Alanı", callback_data="vk_checkbox_menu"),
            InlineKeyboardButton("📝 Not Defteri", callback_data="vk_notepad")
        ],
        [
            InlineKeyboardButton("🤖 GUI Kontrol", callback_data="gui_menu"),
            InlineKeyboardButton("📊 İstatistikler", callback_data="user_stats")
        ],
        [
            InlineKeyboardButton("👑 Admin Panel", callback_data="vk_admin_panel"),
            InlineKeyboardButton("🆘 Yardım", callback_data="help_main")
        ],
        [
            InlineKeyboardButton("ℹ️ Bot Bilgisi", callback_data="bot_info"),
            InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings_menu")
        ]
    ]
    
    # Desteklenen platformları listele
    supported_platforms = "📺 YouTube • 📸 Instagram"
    if ADVANCED_FEATURES_ENABLED:
        supported_platforms += " • 🎵 TikTok • 🐦 Twitter • 👥 Facebook"
    
    await message.reply_text(
        f"🤖 **Naofumi Telegram Bot'a Hoş Geldiniz!** 🤖\n\n"
        f"🎯 **Özellikler:**\n"
        f"• 📺 Video indirme\n"
        f"• 🎵 MP3/MP4 format desteği\n"
        f"• ⚡ Hızlı indirme modu\n"
        f"• ⌨️ Sanal klavye\n"
        f"• 👑 Admin paneli\n"
        f"• 📊 İstatistikler\n\n"
        f"🚀 **Kullanım:**\n"
        f"Video linkini gönderin ve format seçin!\n\n"
        f"💡 **Desteklenen Platformlar:**\n"
        f"{supported_platforms}\n\n"
        f"🆘 **Yardım için /help komutunu kullanın.**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=None
    )

@app.on_message(filters.command("help"))
async def help_command(client, message):
    """
    🆘 /help komutu ile yardım mesajı gönderilir.
    """
    await message.reply_text(
        "🆘 **Yardım Menüsü** 🆘\n\n"
        "**📋 Temel Komutlar:**\n"
        "• `/start` - Bot'u başlat\n"
        "• `/help` - Bu yardım menüsü\n"
        "• `/stats` - Bot istatistikleri\n\n"
        "**🎯 Video İndirme:**\n"
        "• Video linkini gönderin\n"
        "• Format seçin (MP3/MP4)\n"
        "• İndirme otomatik başlar\n\n"
        "**⚡ Hızlı İndirme:**\n"
        "• `fast:link` - Hızlı MP3 indirme\n"
        "• `hızlı:link` - Hızlı MP3 indirme\n"
        "• `quick:link` - Hızlı MP3 indirme\n\n"
        "**⌨️ Sanal Klavye:**\n"
        "• Tıklamalı klavye\n"
        "• Checkbox alanı\n"
        "• Not defteri\n\n"
        "**👑 Admin Komutları:**\n"
        "• `/admin_stats` - Admin istatistikleri\n"
        "• `/admin_users` - Kullanıcı listesi\n"
        "• `/admin_settings` - Bot ayarları\n\n"
        "**📞 Destek:**\n"
        "Sorun yaşarsanız admin ile iletişime geçin.",
        parse_mode=None
    )

@app.on_message(filters.text & ~filters.create(lambda _, __, message: message.text.startswith('/')))
async def send_format_buttons(client, message):
    """
    🔗 Kullanıcı metin mesajı gönderdiğinde URL kontrolü yapılır ve 
       uygun format seçenekleri sunulur.
    """
    text = message.text.strip()
    
    try:
        logger.info(f"Mesaj alındı: {text}")
        
        # Bot mesajlarını filtrele - sonsuz döngüyü önle
        if (text.startswith('❌') or 
            text.startswith('🔍') or 
            text.startswith('✅') or
            text.startswith('🔄') or
            text.startswith('⏱️') or
            text.startswith('📊') or
            text.startswith('📁') or
            text.startswith('🎵') or
            text.startswith('📤') or
            text.startswith('Lütfen bekleyin') or
            text.startswith('Hata:') or
            text.startswith('**Hata:**') or
            text.startswith('**Sanatçı:**') or
            text.startswith('**Çözüm:**') or
            text.startswith('•') or
            text.startswith('Örnek:') or
            'YouTube Bot Koruması' in text or
            'Sanatçı Arama Hatası' in text or
            'Video İndirme Hatası' in text or
            'Çok Fazla İstek' in text):
            logger.info("Bot mesajı filtrelendi, işlenmeyecek")
            return
        
        # Sanatçı ismi ile arama kontrolü - hata mesajlarını filtrele
        if (not any(domain in text.lower() for domain in ['youtube.com', 'youtu.be', 'tiktok.com', 'twitter.com', 'x.com', 'facebook.com', 'fb.watch', 'instagram.com']) 
            and not text.startswith('❌') 
            and not text.startswith('🔍') 
            and not text.startswith('✅')
            and not text.startswith('🔄')
            and not text.startswith('⏱️')
            and not text.startswith('📊')
            and not text.startswith('📁')
            and not text.startswith('🎵')
            and not text.startswith('📤')
            and not text.startswith('Lütfen bekleyin')
            and not text.startswith('Hata:')
            and not text.startswith('**Hata:**')
            and not text.startswith('**Sanatçı:**')
            and not text.startswith('**Çözüm:**')
            and not text.startswith('•')
            and not text.startswith('Örnek:')):
            # URL değilse ve hata mesajı değilse, sanatçı ismi olarak kabul et
            await handle_artist_search(client, message, text)
            return
        
        # Instagram kontrolü
        if "instagram.com" in text.lower():
            await message.reply_text(
                "🚫 **Instagram Geçici Olarak Devre Dışı** 🚫\n\n"
                "Instagram güvenlik önlemleri nedeniyle geçici olarak devre dışı bırakıldı.\n\n"
                "✅ **Desteklenen Platformlar:**\n"
                "• YouTube - Tam destek\n"
                "• TikTok - Tam destek\n"
                "• Twitter - Tam destek\n"
                "• Facebook - Tam destek\n\n"
                "💡 **Alternatif:** Instagram videolarını YouTube'a yükleyip oradan indirebilirsiniz.\n\n"
                "🔄 Instagram desteği yakında geri gelecek!",
                parse_mode=None
            )
            return
        
        # Hızlı indirme modu kontrolü
        if text.lower().startswith(("fast:", "hızlı:", "quick:")):
            url = text.split(":", 1)[1].strip()
            await handle_fast_download(client, message, url)
            return
        
        # URL'yi text olarak kullan
        url = text
        
        # Platform tespiti
        platform = None
        if ADVANCED_FEATURES_ENABLED:
            platform = advanced_features.detect_platform(url)
        
        # Eğer advanced features devre dışıysa, basit URL kontrolü yap
        if not platform:
            if any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'tiktok.com', 'twitter.com', 'x.com', 'facebook.com', 'fb.watch']):
                platform = 'youtube' if 'youtube' in url.lower() or 'youtu.be' in url.lower() else 'unknown'
            else:
                await message.reply_text(
                    "❌ **Desteklenmeyen Platform!** ❌\n\n"
                    "Lütfen geçerli bir video linki gönderin:\n"
                    "• YouTube\n"
                    "• TikTok\n"
                    "• Twitter\n"
                    "• Facebook",
                    parse_mode=None
                )
                return
        
        # ReisMp3_bot gibi direkt indirme yap
        await handle_direct_download(client, message, url, platform)
        
    except Exception as e:
        logger.error(f"Format butonları gönderilirken hata: {e}")
        await message.reply_text(f"❌ **Hata:** {e}")

async def handle_direct_download(client, message, url, platform):
    """
    🚀 ReisMp3_bot gibi direkt indirme - format seçimi yapmadan
    """
    try:
        logger.info(f"Direkt indirme: {url}")
        
        # Platform emojisi
        platform_emoji = "🎬"
        if ADVANCED_FEATURES_ENABLED and platform:
            platform_emoji = advanced_features.get_platform_emoji(platform)
        
        # İndirme mesajı gönder
        status_msg = await message.reply_text(f"{platform_emoji} **Video indiriliyor...**\n\nLütfen bekleyin...")
        
        # yt-dlp ayarları - YouTube bot koruması bypass (Alternatif yöntem)
        ydl_opts = {
            'outtmpl': '/tmp/%(title)s.%(ext)s',  # Render.com'da /tmp kullan
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'socket_timeout': 120,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'quiet': True,
            # YouTube bot koruması için alternatif ayarlar
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_music', 'android_creator', 'android', 'web'],
                    'comment_sort': ['top'],
                    'max_comments': [0],
                    'include_live_chat': False,
                    'skip_download': False,
                    'age_limit': [0],
                    'geo_bypass': True,
                    'geo_bypass_country': 'US'
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            'sleep_interval': 5,
            'max_sleep_interval': 20,
            'sleep_interval_requests': 5,
            'sleep_interval_subtitles': 5,
            'concurrent_fragment_downloads': 1,
            'throttled_rate': '500K',
            # Alternatif çözümler
            'cookiesfrombrowser': None,
            'cookiefile': None,
            'no_check_certificate': True,
            'prefer_insecure': False,
        }
        
        # Format ayarları - MP3 olarak indir
        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        
        start_time = time.time()
        
        # Gelişmiş bypass sistemi - 5 farklı yöntem
        success = False
        info_dict = None
        file_name = None
        
        # 1. Deneme - Android Music Client
        if not success:
            try:
                logger.info("1. Deneme - Android Music Client")
                ydl_opts_1 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_music'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_1) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ 1. Deneme başarılı - Android Music Client")
            except Exception as e:
                logger.warning(f"1. Deneme başarısız: {e}")
        
        # 2. Deneme - iPhone Safari
        if not success:
            try:
                logger.info("2. Deneme - iPhone Safari")
                ydl_opts_2 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_2) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ 2. Deneme başarılı - iPhone Safari")
            except Exception as e:
                logger.warning(f"2. Deneme başarısız: {e}")
        
        # 3. Deneme - Googlebot
        if not success:
            try:
                logger.info("3. Deneme - Googlebot")
                ydl_opts_3 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.google.com/',
                        'Origin': 'https://www.google.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_3) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ 3. Deneme başarılı - Googlebot")
            except Exception as e:
                logger.warning(f"3. Deneme başarısız: {e}")
        
        # 4. Deneme - Firefox
        if not success:
            try:
                logger.info("4. Deneme - Firefox")
                ydl_opts_4 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com',
                        'DNT': '1',
                        'Upgrade-Insecure-Requests': '1'
                    }
                }
                
                with YoutubeDL(ydl_opts_4) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ 4. Deneme başarılı - Firefox")
            except Exception as e:
                logger.warning(f"4. Deneme başarısız: {e}")
        
        # 5. Deneme - Minimal ayarlar
        if not success:
            try:
                logger.info("5. Deneme - Minimal ayarlar")
                ydl_opts_5 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 60,
                    'retries': 1,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
                    }
                }
                
                with YoutubeDL(ydl_opts_5) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ 5. Deneme başarılı - Minimal ayarlar")
            except Exception as e:
                logger.warning(f"5. Deneme başarısız: {e}")
        
        # Eğer hiçbir deneme başarılı olmadıysa
        if not success:
            raise Exception("Tüm bypass yöntemleri başarısız oldu. YouTube bot koruması çok güçlü.")
        
        # Render.com uyumlu dosya kontrolü
        try:
            file_name = find_downloaded_file(file_name, "İndirme")
        except Exception as e:
            logger.error(f"İndirme - Dosya bulunamadı: {e}")
            raise Exception("Dosya indirilemedi!")
        
        # Thumbnail indirme
        thumbnail_url = info_dict.get('thumbnail')
        thumbnail_file = None
        if thumbnail_url:
            try:
                thumbnail_file = f"/tmp/{os.path.basename(file_name)}_thumb.jpg"
                response = requests.get(thumbnail_url)
                with open(thumbnail_file, 'wb') as f:
                    f.write(response.content)
            except:
                thumbnail_file = None
        
        # Dosya boyutu ve süre
        file_size = os.path.getsize(file_name)
        elapsed_time = time.time() - start_time
        file_size_mb = file_size / (1024 * 1024)
        
        await status_msg.edit_text(
            f"✅ **İndirme Tamamlandı!** ✅\n\n"
            f"🎵 **Başlık:** {info_dict.get('title', 'Audio')}\n"
            f"📁 **Dosya:** {os.path.basename(file_name)}\n"
            f"📊 **Boyut:** {file_size_mb:.1f} MB\n"
            f"⏱️ **Süre:** {int(elapsed_time)} saniye\n"
            f"📤 **Gönderiliyor...**"
        )
        
        # Dosya gönderme
        title = f"{info_dict.get('title', 'Audio')} - MP3"
        await send_file(client, message.chat.id, file_name, title, status_msg, thumbnail_file)
        
        # Geçici dosyaları temizle
        try:
            if thumbnail_file and os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Direkt indirme hatası: {e}", exc_info=True)
        bot_stats['total_errors'] += 1
        
        # Hata türüne göre özel mesaj - sadece bir kez gönder
        try:
            error_msg = str(e).lower()
            if "sign in to confirm" in error_msg or "bot" in error_msg:
                await message.reply_text(
                    "❌ **YouTube Bot Koruması Tespit Edildi**\n\n"
                    "YouTube geçici olarak bot erişimini engelliyor.\n\n"
                    "🔄 **Çözümler:**\n"
                    "• Birkaç dakika bekleyip tekrar deneyin\n"
                    "• Farklı bir video linki deneyin\n"
                    "• Bot yeniden başlatılıyor...\n\n"
                    "⏱️ **Tahmini süre:** 5-10 dakika"
                )
            elif "429" in error_msg or "too many requests" in error_msg:
                await message.reply_text(
                    "❌ **Çok Fazla İstek**\n\n"
                    "YouTube çok fazla istek aldığı için geçici olarak engelliyor.\n\n"
                    "🔄 **Çözüm:**\n"
                    "• 10-15 dakika bekleyin\n"
                    "• Daha sonra tekrar deneyin"
                )
            else:
                await message.reply_text(
                    f"❌ **Video İndirme Hatası**\n\n"
                    f"**Hata:** {str(e)[:100]}...\n\n"
                    f"🔄 **Çözüm:**\n"
                    f"• Lütfen tekrar deneyin\n"
                    f"• Farklı bir video linki kullanın\n"
                    f"• Sorun devam ederse admin ile iletişime geçin"
                )
        except Exception as reply_error:
            logger.error(f"Hata mesajı gönderilemedi: {reply_error}")
            # Hata mesajı gönderilemezse sessizce geç


async def handle_artist_search(client, message, artist_name):
    """
    🎵 Sanatçı ismi ile YouTube'da arama yapıp en popüler sonucu indirir
    """
    try:
        logger.info(f"Sanatçı arama: {artist_name}")
        
        # Arama mesajı gönder
        search_msg = await message.reply_text(f"🔍 **'{artist_name}' aranıyor...**\n\nLütfen bekleyin...")
        
        # YouTube'da arama yap
        search_query = f"ytsearch1:{artist_name}"
        
        # yt-dlp ile arama
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '/tmp/%(title)s.%(ext)s',
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'socket_timeout': 120,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_music', 'android_creator', 'android', 'web'],
                    'comment_sort': ['top'],
                    'max_comments': [0],
                    'include_live_chat': False,
                    'skip_download': False,
                    'age_limit': [0],
                    'geo_bypass': True,
                    'geo_bypass_country': 'US'
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            'sleep_interval': 5,
            'max_sleep_interval': 20,
            'sleep_interval_requests': 5,
            'sleep_interval_subtitles': 5,
            'concurrent_fragment_downloads': 1,
            'throttled_rate': '500K',
            'cookiesfrombrowser': None,
            'cookiefile': None,
            'no_check_certificate': True,
            'prefer_insecure': False,
        }
        
        start_time = time.time()
        
        # Gelişmiş bypass sistemi - 5 farklı yöntem
        success = False
        info_dict = None
        file_name = None
        
        # 1. Deneme - Android Music Client
        if not success:
            try:
                logger.info("Sanatçı arama - 1. Deneme - Android Music Client")
                ydl_opts_1 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android_music'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_1) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ Sanatçı arama - 1. Deneme başarılı - Android Music Client")
            except Exception as e:
                logger.warning(f"Sanatçı arama - 1. Deneme başarısız: {e}")
        
        # 2. Deneme - iPhone Safari
        if not success:
            try:
                logger.info("Sanatçı arama - 2. Deneme - iPhone Safari")
                ydl_opts_2 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_2) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ Sanatçı arama - 2. Deneme başarılı - iPhone Safari")
            except Exception as e:
                logger.warning(f"Sanatçı arama - 2. Deneme başarısız: {e}")
        
        # 3. Deneme - Googlebot
        if not success:
            try:
                logger.info("Sanatçı arama - 3. Deneme - Googlebot")
                ydl_opts_3 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.google.com/',
                        'Origin': 'https://www.google.com'
                    }
                }
                
                with YoutubeDL(ydl_opts_3) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ Sanatçı arama - 3. Deneme başarılı - Googlebot")
            except Exception as e:
                logger.warning(f"Sanatçı arama - 3. Deneme başarısız: {e}")
        
        # 4. Deneme - Firefox
        if not success:
            try:
                logger.info("Sanatçı arama - 4. Deneme - Firefox")
                ydl_opts_4 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 180,
                    'retries': 3,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web'],
                            'geo_bypass': True,
                            'geo_bypass_country': 'US'
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.youtube.com/',
                        'Origin': 'https://www.youtube.com',
                        'DNT': '1',
                        'Upgrade-Insecure-Requests': '1'
                    }
                }
                
                with YoutubeDL(ydl_opts_4) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ Sanatçı arama - 4. Deneme başarılı - Firefox")
            except Exception as e:
                logger.warning(f"Sanatçı arama - 4. Deneme başarısız: {e}")
        
        # 5. Deneme - Minimal ayarlar
        if not success:
            try:
                logger.info("Sanatçı arama - 5. Deneme - Minimal ayarlar")
                ydl_opts_5 = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 60,
                    'retries': 1,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
                    }
                }
                
                with YoutubeDL(ydl_opts_5) as ydl:
                    info_dict = ydl.extract_info(search_query, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
                    success = True
                    logger.info("✅ Sanatçı arama - 5. Deneme başarılı - Minimal ayarlar")
            except Exception as e:
                logger.warning(f"Sanatçı arama - 5. Deneme başarısız: {e}")
        
        # Eğer hiçbir deneme başarılı olmadıysa
        if not success:
            raise Exception("Tüm bypass yöntemleri başarısız oldu. YouTube bot koruması çok güçlü.")
        
        # Render.com uyumlu dosya kontrolü
        try:
            file_name = find_downloaded_file(file_name, "İndirme")
        except Exception as e:
            logger.error(f"İndirme - Dosya bulunamadı: {e}")
            raise Exception("Dosya indirilemedi!")
        
        # Thumbnail indirme
        thumbnail_url = info_dict.get('thumbnail')
        thumbnail_file = None
        if thumbnail_url:
            try:
                thumbnail_file = f"/tmp/{os.path.basename(file_name)}_thumb.jpg"
                response = requests.get(thumbnail_url)
                with open(thumbnail_file, 'wb') as f:
                    f.write(response.content)
            except:
                thumbnail_file = None
        
        # Dosya boyutu ve süre
        file_size = os.path.getsize(file_name)
        elapsed_time = time.time() - start_time
        file_size_mb = file_size / (1024 * 1024)
        
        await search_msg.edit_text(
            f"✅ **Arama Tamamlandı!** ✅\n\n"
            f"🎵 **Sanatçı:** {artist_name}\n"
            f"📁 **Dosya:** {os.path.basename(file_name)}\n"
            f"📊 **Boyut:** {file_size_mb:.1f} MB\n"
            f"⏱️ **Süre:** {int(elapsed_time)} saniye\n"
            f"📤 **Gönderiliyor...**"
        )
        
        # Dosya gönderme
        title = f"{info_dict.get('title', 'Audio')} - {artist_name}"
        await send_file(client, message.chat.id, file_name, title, search_msg, thumbnail_file)
        
        # Geçici dosyaları temizle
        try:
            if thumbnail_file and os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Sanatçı arama hatası: {e}", exc_info=True)
        bot_stats['total_errors'] += 1
        
        # Hata türüne göre özel mesaj - sadece bir kez gönder
        try:
            error_msg = str(e).lower()
            if "sign in to confirm" in error_msg or "bot" in error_msg:
                await message.reply_text(
                    "❌ **YouTube Bot Koruması Tespit Edildi**\n\n"
                    "YouTube geçici olarak bot erişimini engelliyor.\n\n"
                    "🔄 **Çözümler:**\n"
                    "• Birkaç dakika bekleyip tekrar deneyin\n"
                    "• Farklı bir sanatçı ismi deneyin\n"
                    "• Bot yeniden başlatılıyor...\n\n"
                    "⏱️ **Tahmini süre:** 5-10 dakika"
                )
            elif "429" in error_msg or "too many requests" in error_msg:
                await message.reply_text(
                    "❌ **Çok Fazla İstek**\n\n"
                    "YouTube çok fazla istek aldığı için geçici olarak engelliyor.\n\n"
                    "🔄 **Çözüm:**\n"
                    "• 10-15 dakika bekleyin\n"
                    "• Daha sonra tekrar deneyin"
                )
            else:
                await message.reply_text(
                    f"❌ **Sanatçı Arama Hatası**\n\n"
                    f"**Sanatçı:** {artist_name}\n"
                    f"**Hata:** {str(e)[:100]}...\n\n"
                    f"🔄 **Çözüm:**\n"
                    f"• Farklı bir sanatçı ismi deneyin\n"
                    f"• Daha spesifik arama yapın\n"
                    f"• Örnek: 'Ed Sheeran Shape of You'"
                )
        except Exception as reply_error:
            logger.error(f"Hata mesajı gönderilemedi: {reply_error}")
            # Hata mesajı gönderilemezse sessizce geç

async def handle_fast_download(client, message, url):
    """
    ⚡ Hızlı indirme modu - ReisMp3_bot gibi tek tıkla indirme
    """
    try:
        # Platform tespiti
        platform = None
        if ADVANCED_FEATURES_ENABLED:
            platform = advanced_features.detect_platform(url)
        
        # Hızlı indirme için varsayılan ayarlar
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'socket_timeout': 120,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'quiet': True,
            # YouTube bot koruması için alternatif ayarlar
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_music', 'android_creator', 'android', 'web'],
                    'comment_sort': ['top'],
                    'max_comments': [0],
                    'include_live_chat': False,
                    'skip_download': False,
                    'age_limit': [0],
                    'geo_bypass': True,
                    'geo_bypass_country': 'US'
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            'sleep_interval': 5,
            'max_sleep_interval': 20,
            'sleep_interval_requests': 5,
            'sleep_interval_subtitles': 5,
            'concurrent_fragment_downloads': 1,
            'throttled_rate': '500K',
            # Alternatif çözümler
            'cookiesfrombrowser': None,
            'cookiefile': None,
            'no_check_certificate': True,
            'prefer_insecure': False,
        }
        
        # Platform emojisi
        platform_emoji = "🎬"
        if ADVANCED_FEATURES_ENABLED and platform:
            platform_emoji = advanced_features.get_platform_emoji(platform)
        
        status_msg = await message.reply_text(f"{platform_emoji} **Hızlı İndirme Başladı!** ⚡\n\nLütfen bekleyin...")
        
        start_time = time.time()
        
        # İlk deneme - normal yt-dlp
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info_dict)
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"
        except Exception as e:
            logger.warning(f"Hızlı indirme - İlk yt-dlp denemesi başarısız: {e}")
            
            # İkinci deneme - farklı ayarlarla
            logger.info("Hızlı indirme - Alternatif yt-dlp ayarları deneniyor...")
            ydl_opts_alt = ydl_opts.copy()
            ydl_opts_alt['extractor_args']['youtube']['player_client'] = ['android', 'web']
            ydl_opts_alt['http_headers']['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
            
            try:
                with YoutubeDL(ydl_opts_alt) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            except Exception as e2:
                logger.warning(f"Hızlı indirme - İkinci yt-dlp denemesi başarısız: {e2}")
                
                # Üçüncü deneme - minimal ayarlarla
                logger.info("Hızlı indirme - Minimal yt-dlp ayarları deneniyor...")
                ydl_opts_minimal = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '%(title)s.%(ext)s',
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False,
                    'socket_timeout': 60,
                    'retries': 2,
                    'no_warnings': True,
                    'quiet': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                    }
                }
                
                with YoutubeDL(ydl_opts_minimal) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    file_name = ydl.prepare_filename(info_dict)
                    file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            
            # Render.com uyumlu dosya kontrolü - Hızlı indirme
            try:
                file_name = find_downloaded_file(file_name, "Hızlı indirme")
            except Exception as e:
                logger.error(f"Hızlı indirme - Dosya bulunamadı: {e}")
                raise Exception("Dosya indirilemedi!")
            
            # Thumbnail indirme
            thumbnail_url = info_dict.get('thumbnail')
            thumbnail_file = None
            if thumbnail_url:
                try:
                    thumbnail_file = f"{file_name}_thumb.jpg"
                    response = requests.get(thumbnail_url)
                    with open(thumbnail_file, 'wb') as f:
                        f.write(response.content)
                except:
                    thumbnail_file = None
            
            # Dosya boyutu ve süre
            file_size = os.path.getsize(file_name)
            elapsed_time = time.time() - start_time
            file_size_mb = file_size / (1024 * 1024)
            
            await status_msg.edit_text(
                f"✅ **İndirme Tamamlandı!** ✅\n\n"
                f"📁 **Dosya:** {os.path.basename(file_name)}\n"
                f"📊 **Boyut:** {file_size_mb:.1f} MB\n"
                f"⏱️ **Süre:** {int(elapsed_time)} saniye\n"
                f"📤 **Gönderiliyor...**"
            )
            
            # Dosya gönderme
            title = f"{info_dict.get('title', 'Audio')} - Hızlı İndirme"
            await send_file(client, message.chat.id, file_name, title, status_msg, thumbnail_file)
            
    except Exception as e:
        logger.error(f"Hızlı indirme hatası: {e}", exc_info=True)
        bot_stats['total_errors'] += 1
        
        # Hata türüne göre özel mesaj
        error_msg = str(e).lower()
        if "sign in to confirm" in error_msg or "bot" in error_msg:
            await message.reply_text(
                "❌ **YouTube Bot Koruması Tespit Edildi**\n\n"
                "YouTube geçici olarak bot erişimini engelliyor.\n\n"
                "🔄 **Çözümler:**\n"
                "• Birkaç dakika bekleyip tekrar deneyin\n"
                "• Farklı bir video linki deneyin\n"
                "• Bot yeniden başlatılıyor...\n\n"
                "⏱️ **Tahmini süre:** 5-10 dakika"
            )
        elif "429" in error_msg or "too many requests" in error_msg:
            await message.reply_text(
                "❌ **Çok Fazla İstek**\n\n"
                "YouTube çok fazla istek aldığı için geçici olarak engelliyor.\n\n"
                "🔄 **Çözüm:**\n"
                "• 10-15 dakika bekleyin\n"
                "• Daha sonra tekrar deneyin"
            )
        else:
            await message.reply_text(
                f"❌ **Hızlı İndirme Hatası**\n\n"
                f"**Hata:** {str(e)[:200]}...\n\n"
                f"🔄 **Çözüm:**\n"
                f"• Lütfen tekrar deneyin\n"
                f"• Farklı bir video linki kullanın"
            )

######################################
#         CALLBACK HANDLERS          #
######################################

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    """
    🔘 Callback query'leri işler - TÜM BUTONLAR
    """
    data = callback_query.data
    message = callback_query.message
    user_id = callback_query.from_user.id
    
    try:
        # ======================
        # ANA MENÜ BUTONLARI
        # ======================
        
        if data == "fast_download":
            await callback_query.edit_message_text(
                "⚡ **Hızlı İndirme Modu** ⚡\n\n"
                "Video linkini şu şekilde gönderin:\n"
                "• `fast:https://youtu.be/...`\n"
                "• `hızlı:https://youtu.be/...`\n"
                "• `quick:https://youtu.be/...`\n\n"
                "📺 **Desteklenen Platformlar:**\n"
                "• YouTube\n"
                "• TikTok\n"
                "• Twitter\n"
                "• Facebook\n\n"
                "Bot otomatik olarak 192kbps MP3 indirecek!",
                parse_mode=None
            )
            await callback_query.answer("⚡ Link bekleniyor...")
            return
        
        elif data == "quick_download":
            keyboard = [
                [InlineKeyboardButton("🎵 MP3 (192kbps)", callback_data="quick_mp3")],
                [InlineKeyboardButton("📺 MP4 (720p)", callback_data="quick_mp4")],
                [InlineKeyboardButton("🔙 Geri", callback_data="start_menu")]
            ]
            await callback_query.edit_message_text(
                "📺 **Hızlı Video İndirme**\n\n"
                "Format seçin ve ardından linki gönderin:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await callback_query.answer("📺 Format seçin")
            return
        
        elif data == "user_stats":
            if ADMIN_PANEL_ENABLED:
                stats = admin_panel.stats
                uptime = time.time() - stats.get('start_time', time.time())
                uptime_str = str(timedelta(seconds=int(uptime)))
                
                user_activity = stats.get('user_activity', {}).get(str(user_id), {})
                total_commands = user_activity.get('total_commands', 0)
                total_downloads = user_activity.get('downloads', 0)
                
                await callback_query.edit_message_text(
                    f"📊 **Kişisel İstatistikleriniz**\n\n"
                    f"🆔 **User ID:** `{user_id}`\n"
                    f"⚡ **Komut Sayısı:** {total_commands}\n"
                    f"📥 **İndirme Sayısı:** {total_downloads}\n"
                    f"⏱️ **Bot Uptime:** {uptime_str}\n\n"
                    f"🌟 **Bot İstatistikleri:**\n"
                    f"👥 Toplam Kullanıcı: {len(stats.get('user_activity', {}))}\n"
                    f"📥 Toplam İndirme: {stats.get('total_downloads', 0)}"
                )
            else:
                await callback_query.edit_message_text("📊 İstatistikler şu an mevcut değil.")
            await callback_query.answer("📊 İstatistikler yüklendi")
            return
        
        elif data == "bot_info":
            await callback_query.edit_message_text(
                "🤖 **Naofumi Telegram Bot**\n\n"
                "📌 **Versiyon:** 2.0.0\n"
                "👨‍💻 **Geliştirici:** @YourUsername\n"
                "🚀 **Platform:** Render.com\n\n"
                "🎯 **Özellikler:**\n"
                "✅ YouTube İndirme\n"
                f"{'✅' if ADVANCED_FEATURES_ENABLED else '❌'} TikTok İndirme\n"
                f"{'✅' if ADVANCED_FEATURES_ENABLED else '❌'} Twitter İndirme\n"
                f"{'✅' if VIRTUAL_KEYBOARD_ENABLED else '❌'} Sanal Klavye\n"
                f"{'✅' if ADMIN_PANEL_ENABLED else '❌'} Admin Panel\n\n"
                "💡 Bot sürekli geliştirilmektedir!"
            )
            await callback_query.answer("ℹ️ Bot bilgisi")
            return
        
        elif data == "help_main":
            await callback_query.edit_message_text(
                "🆘 **Yardım Menüsü**\n\n"
                "**📋 Temel Kullanım:**\n"
                "1. Video linkini gönderin\n"
                "2. Format seçin (MP3/MP4)\n"
                "3. Kalite seçin\n"
                "4. İndirin!\n\n"
                "**⚡ Hızlı İndirme:**\n"
                "`fast:link` yazarak direkt MP3 indirin\n\n"
                "**⌨️ Sanal Klavye:**\n"
                "Tıklamalı klavye ile metin yazın\n\n"
                "**📞 Destek:**\n"
                "Sorun yaşarsanız /start ile başa dönün"
            )
            await callback_query.answer("🆘 Yardım")
            return
        
        elif data == "settings_menu":
            keyboard = [
                [InlineKeyboardButton("🌐 Dil Ayarları", callback_data="settings_lang")],
                [InlineKeyboardButton("🔔 Bildirimler", callback_data="settings_notif")],
                [InlineKeyboardButton("📁 İndirme Ayarları", callback_data="settings_download")],
                [InlineKeyboardButton("🔙 Ana Menü", callback_data="start_menu")]
            ]
            await callback_query.edit_message_text(
                "⚙️ **Ayarlar Menüsü**\n\n"
                "Lütfen bir ayar kategorisi seçin:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await callback_query.answer("⚙️ Ayarlar")
            return
        
        elif data == "start_menu":
            # Ana menüye dön
            keyboard = [
                [
                    InlineKeyboardButton("⚡ Hızlı İndirme", callback_data="fast_download"),
                    InlineKeyboardButton("📺 Video İndir", callback_data="quick_download"),
                    InlineKeyboardButton("⌨️ Sanal Klavye", callback_data="vk_main_menu")
                ],
                [
                    InlineKeyboardButton("☑️ Checkbox Alanı", callback_data="vk_checkbox_menu"),
                    InlineKeyboardButton("📝 Not Defteri", callback_data="vk_notepad")
                ],
                [
                    InlineKeyboardButton("🤖 GUI Kontrol", callback_data="gui_menu"),
                    InlineKeyboardButton("📊 İstatistikler", callback_data="user_stats")
                ],
                [
                    InlineKeyboardButton("👑 Admin Panel", callback_data="vk_admin_panel"),
                    InlineKeyboardButton("🆘 Yardım", callback_data="help_main")
                ],
                [
                    InlineKeyboardButton("ℹ️ Bot Bilgisi", callback_data="bot_info"),
                    InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings_menu")
                ]
            ]
            await callback_query.edit_message_text(
                "🤖 **Ana Menü**\n\n"
                "Bir seçenek seçin:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await callback_query.answer("🏠 Ana menü")
            return
        
        # ======================
        # VIRTUAL KEYBOARD
        # ======================
        
        elif data == "vk_main_menu" or data == "vk_letters":
            if VIRTUAL_KEYBOARD_ENABLED:
                keyboard = virtual_keyboard.get_quick_keyboard()
                current_text = virtual_keyboard.get_current_text()
                await callback_query.edit_message_text(
                    f"⌨️ **Sanal Klavye**\n\n"
                    f"📝 **Metin:** {current_text if current_text else '(boş)'}\n\n"
                    f"Bir seçenek seçin:",
                    reply_markup=keyboard
                )
                await callback_query.answer("⌨️ Sanal klavye açıldı")
            else:
                await callback_query.answer("⌨️ Sanal klavye devre dışı", show_alert=True)
            return
        
        elif data == "vk_numbers":
            if VIRTUAL_KEYBOARD_ENABLED:
                keyboard = virtual_keyboard.get_numbers_keyboard()
                current_text = virtual_keyboard.get_current_text()
                await callback_query.edit_message_text(
                    f"🔢 **Sayı Klavyesi**\n\n"
                    f"📝 **Metin:** {current_text if current_text else '(boş)'}",
                    reply_markup=keyboard
                )
                await callback_query.answer("🔢 Sayı klavyesi")
            return
        
        elif data == "vk_symbols":
            if VIRTUAL_KEYBOARD_ENABLED:
                keyboard = virtual_keyboard.get_symbols_keyboard()
                current_text = virtual_keyboard.get_current_text()
                await callback_query.edit_message_text(
                    f"🌐 **Sembol Klavyesi**\n\n"
                    f"📝 **Metin:** {current_text if current_text else '(boş)'}",
                    reply_markup=keyboard
                )
                await callback_query.answer("🌐 Sembol klavyesi")
            return
        
        elif data.startswith("vk_key_"):
            if VIRTUAL_KEYBOARD_ENABLED:
                virtual_keyboard.process_key(data)
                current_text = virtual_keyboard.get_current_text()
                await callback_query.answer(f"Yazıldı: {current_text[-1] if current_text else ''}")
            return
        
        elif data == "vk_checkbox_menu":
            if VIRTUAL_KEYBOARD_ENABLED:
                keyboard = virtual_keyboard.get_checkbox_keyboard()
                summary = virtual_keyboard.get_checkbox_summary()
                await callback_query.edit_message_text(
                    f"☑️ **Checkbox Alanı**\n\n{summary}",
                    reply_markup=keyboard
                )
                await callback_query.answer("☑️ Checkbox menüsü")
            return
        
        elif data == "vk_notepad":
            if VIRTUAL_KEYBOARD_ENABLED:
                keyboard = virtual_keyboard.get_notepad_keyboard()
                summary = virtual_keyboard.get_notes_summary()
                await callback_query.edit_message_text(
                    f"📝 **Not Defteri**\n\n{summary}",
                    reply_markup=keyboard
                )
                await callback_query.answer("📝 Not defteri")
            return
        
        elif data == "vk_close":
            await callback_query.message.delete()
            await callback_query.answer("❌ Kapatıldı")
            return
        
        # ======================
        # ADMIN PANEL
        # ======================
        
        elif data == "vk_admin_panel":
            if ADMIN_PANEL_ENABLED and admin_panel.is_admin(user_id):
                keyboard = admin_panel.get_admin_keyboard()
                await callback_query.edit_message_text(
                    "👑 **Admin Panel**\n\n"
                    "Yönetim işlemlerini seçin:",
                    reply_markup=keyboard
                )
                await callback_query.answer("👑 Admin panel")
            else:
                await callback_query.answer("❌ Admin yetkisi gerekli!", show_alert=True)
            return
        
        elif data == "vk_admin_stats":
            if ADMIN_PANEL_ENABLED and admin_panel.is_admin(user_id):
                stats_text = admin_panel.get_admin_stats()
                await callback_query.edit_message_text(stats_text)
                await callback_query.answer("📊 İstatistikler yüklendi")
            return
        
        elif data == "vk_admin_users":
            if ADMIN_PANEL_ENABLED and admin_panel.is_admin(user_id):
                users_text = admin_panel.get_user_list()
                await callback_query.edit_message_text(users_text)
                await callback_query.answer("👥 Kullanıcı listesi")
            return
        
        elif data == "vk_admin_settings":
            if ADMIN_PANEL_ENABLED and admin_panel.is_admin(user_id):
                settings_text = admin_panel.get_settings()
                await callback_query.edit_message_text(settings_text)
                await callback_query.answer("⚙️ Ayarlar")
            return
        
        # ======================
        # İNDİRME CALLBACKS
        # ======================
        
        elif data.startswith("mp3_") or data.startswith("mp4_"):
            parts = data.split("_")
            if len(parts) >= 3:
                format_type = parts[0]
                quality = parts[1]
                url_id = "_".join(parts[2:])
                
                url = get_cached_url(url_id)
                if not url:
                    keyboard = [[InlineKeyboardButton("🔄 Linki Tekrar Gönder", callback_data="start_menu")]]
                    await callback_query.edit_message_text(
                        "❌ **URL Bulunamadı!**\n\n"
                        "Bot yeniden başlatıldı, lütfen linki tekrar gönderin.",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    await callback_query.answer("❌ Link tekrar gönderin", show_alert=True)
                    return
                
                await callback_query.answer("📥 İndirme başlıyor...")
                await download_video(client, message, url, format_type, quality)
            return
        
        # ======================
        # VARSAYILAN
        # ======================
        
        else:
            await callback_query.answer("🚧 Bu özellik henüz hazır değil!")
        
    except Exception as e:
        logger.error(f"Callback query hatası: {e}", exc_info=True)
        await callback_query.answer("❌ Hata oluştu!", show_alert=True)

######################################
#           SIGNAL HANDLER           #
######################################
def signal_handler(sig, frame):
    """
    🔔 Kapatma sinyalleri alındığında botu düzgün şekilde sonlandırır.
    """
    print("\n🚪 Kapat komutu alındı. Bot durduruluyor...")
    if app:
        try:
            # Çalışan loop'u kullan
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(app.stop())
            else:
                loop.run_until_complete(app.stop())
        except Exception as e:
            print(f"⚠️ Durdurma uyarısı: {e}")
    sys.exit(0)

def run_bot():
    """Bot'u çalıştır"""
    try:
        logger.info("🚀 Bot başlatılıyor...")
        app.run()
        logger.info("✅ Bot başarıyla başlatıldı!")
    except Exception as e:
        logger.critical(f"🚨 Bot çalıştırılırken kritik hata: {e}", exc_info=True)

def run_web_server():
    """Web sunucusunu çalıştır (Replit/Render.com için)"""
    try:
        logger.info("🌐 Web sunucusu başlatılıyor...")
        port = int(os.getenv('PORT', 5000))
        web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.critical(f"🚨 Web sunucusu başlatılırken hata: {e}", exc_info=True)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Hem bot hem web sunucusunu çalıştır
    import threading
    
    # Web sunucusunu ayrı thread'de çalıştır (daemon=False)
    web_thread = threading.Thread(target=run_web_server, daemon=False)
    web_thread.start()
    
    # Bot'u ana thread'de çalıştır (asyncio için daha güvenli)
    run_bot()