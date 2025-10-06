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
from flask import Flask, jsonify

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
    return jsonify({
        'status': 'healthy',
        'bot_running': True,
        'uptime': time.time() - bot_stats.get('start_time', time.time()),
        'total_downloads': bot_stats.get('total_downloads', 0),
        'total_users': len(bot_stats.get('total_users', set())),
        'timestamp': time.time()
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

# Bot istatistikleri
bot_stats = {
    'start_time': time.time(),
    'total_downloads': 0,
    'total_users': set(),
    'total_errors': 0
}

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
        
        # yt-dlp ayarları
        ydl_opts = {
            'outtmpl': '/tmp/%(title)s.%(ext)s',  # Render.com'da /tmp kullan
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'socket_timeout': 30,
            'retries': 3
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
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            
            # Dosya uzantısını düzelt
            if format_type == 'mp3':
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            else:
                file_name = file_name.rsplit(".", 1)[0] + ".mp4"
            
            # Dosya kontrolü - alternatif yolları dene
            if not os.path.exists(file_name):
                # /tmp klasöründe ara
                base_name = os.path.basename(file_name)
                tmp_file = f"/tmp/{base_name}"
                if os.path.exists(tmp_file):
                    file_name = tmp_file
                else:
                    # Mevcut dizinde ara
                    current_dir_file = os.path.join(os.getcwd(), base_name)
                    if os.path.exists(current_dir_file):
                        file_name = current_dir_file
                    else:
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
        logger.error(f"Video indirme hatası: {e}")
        await message.reply_text(f"❌ **Video indirme hatası:** {e}")

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
    url = message.text.strip()
    
    try:
        logger.info(f"Mesaj alındı: {url}")
        
        # Instagram kontrolü
        if "instagram.com" in url.lower():
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
        if url.lower().startswith(("fast:", "hızlı:", "quick:")):
            url = url.split(":", 1)[1].strip()
            await handle_fast_download(client, message, url)
            return
        
        # Platform tespiti
        platform = None
        if ADVANCED_FEATURES_ENABLED:
            platform = advanced_features.detect_platform(url)
        
        if not platform:
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
        
        # Format seçenekleri
        keyboard = [
            [
                InlineKeyboardButton("🎵 MP3 (128kbps)", callback_data=f"download_mp3_128_{url}"),
                InlineKeyboardButton("🎵 MP3 (192kbps)", callback_data=f"download_mp3_192_{url}")
            ],
            [
                InlineKeyboardButton("🎵 MP3 (256kbps)", callback_data=f"download_mp3_256_{url}"),
                InlineKeyboardButton("🎵 MP3 (320kbps)", callback_data=f"download_mp3_320_{url}")
            ],
            [
                InlineKeyboardButton("📺 MP4 (360p)", callback_data=f"download_mp4_360_{url}"),
                InlineKeyboardButton("📺 MP4 (480p)", callback_data=f"download_mp4_480_{url}")
            ],
            [
                InlineKeyboardButton("📺 MP4 (720p)", callback_data=f"download_mp4_720_{url}"),
                InlineKeyboardButton("📺 MP4 (1080p)", callback_data=f"download_mp4_1080_{url}")
            ]
        ]
        
        platform_emoji = "🎬"
        if ADVANCED_FEATURES_ENABLED and platform:
            platform_emoji = advanced_features.get_platform_emoji(platform)
        
        await message.reply_text(
            f"{platform_emoji} **Platform Tespit Edildi: {platform.upper()}**\n\n"
            f"📋 **Format seçin:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=None
        )
        
    except Exception as e:
        logger.error(f"Format butonları gönderilirken hata: {e}")
        await message.reply_text(f"❌ **Hata:** {e}")

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
            'socket_timeout': 30,
            'retries': 3
        }
        
        # Platform emojisi
        platform_emoji = "🎬"
        if ADVANCED_FEATURES_ENABLED and platform:
            platform_emoji = advanced_features.get_platform_emoji(platform)
        
        status_msg = await message.reply_text(f"{platform_emoji} **Hızlı İndirme Başladı!** ⚡\n\nLütfen bekleyin...")
        
        start_time = time.time()
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            
            # Dosya kontrolü
            if not os.path.exists(file_name):
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
        logger.error(f"Hızlı indirme hatası: {e}")
        await message.reply_text(f"❌ **Hızlı İndirme Hatası:** {e}")

######################################
#         CALLBACK HANDLERS          #
######################################

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    """
    🔘 Callback query'leri işler
    """
    data = callback_query.data
    message = callback_query.message
    
    try:
        # Hızlı indirme
        if data == "fast_download":
            await callback_query.edit_message_text(
                "⚡ **Hızlı İndirme Modu** ⚡\n\n"
                "Video linkini gönderin (ReisMp3_bot gibi):\n"
                "• YouTube\n"
                "• TikTok\n"
                "• Twitter\n"
                "• Facebook\n\n"
                "💡 **Kullanım:**\n"
                "• `fast:https://youtu.be/...` - Hızlı MP3 indirme\n"
                "• `hızlı:https://youtu.be/...` - Hızlı MP3 indirme\n"
                "• `quick:https://youtu.be/...` - Hızlı MP3 indirme\n\n"
                "Bot otomatik olarak 192kbps MP3 indirecek!",
                parse_mode=None
            )
            await callback_query.answer("⚡ Hızlı indirme linki bekleniyor...")
            return
        
        # Download callbacks
        if data.startswith("download_"):
            parts = data.split("_")
            if len(parts) >= 4:
                format_type = parts[1]  # mp3 or mp4
                quality = parts[2]     # 128, 192, 360, etc.
                url = "_".join(parts[3:])  # URL
                
                await callback_query.answer("📥 İndirme başlatılıyor...")
                await download_video(client, message, url, format_type, quality)
                return
        
        # Diğer callback'ler
        await callback_query.answer("🚀 Özellik yakında gelecek!")
        
    except Exception as e:
        logger.error(f"Callback query hatası: {e}")
        await callback_query.answer("❌ Hata oluştu!")

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
            asyncio.run(app.stop())
        except Exception as e:
            print(f"❌ Durdurma sırasında hata: {e}")
    sys.exit(0)

def run_bot():
    """Bot'u çalıştır"""
    try:
        logger.info("🚀 Bot başlatılıyor...")
        # Thread içinde yeni event loop oluştur
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app.run()
    except Exception as e:
        logger.critical(f"🚨 Bot çalıştırılırken kritik hata: {e}", exc_info=True)
        sys.exit(1)

def run_web_server():
    """Web sunucusunu çalıştır (Replit/Render.com için)"""
    try:
        logger.info("🌐 Web sunucusu başlatılıyor...")
        port = int(os.getenv('PORT', 5000))
        web_app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.critical(f"🚨 Web sunucusu başlatılırken hata: {e}", exc_info=True)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Hem bot hem web sunucusunu çalıştır
    import threading
    
    # Bot'u ayrı thread'de çalıştır
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Web sunucusunu ana thread'de çalıştır
    run_web_server()