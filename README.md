# 🤖 kOsEmtRa - Naofumi Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green.svg)](https://pyrogram.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Güçlü ve özellik dolu bir Telegram botu! YouTube, TikTok, Twitter ve Facebook'tan video indirme, sanal klavye, admin paneli ve daha fazlası.

## ✨ Özellikler

### 🎬 Video İndirme
- **YouTube** - Tam destek
- **TikTok** - Tam destek  
- **Twitter** - Tam destek
- **Facebook** - Tam destek
- **Instagram** - Geçici olarak devre dışı

### 🎵 Format Desteği
- **MP3** - 128kbps, 192kbps, 256kbps, 320kbps
- **MP4** - 360p, 480p, 720p, 1080p
- **Otomatik dönüştürme** ve kalite seçimi

### ⚡ Hızlı İndirme
- Tek tıkla MP3 indirme
- `fast:link` komutu ile hızlı erişim
- Otomatik format tespiti

### ⌨️ Sanal Klavye
- Tıklamalı klavye sistemi
- Checkbox alanı
- Not defteri özelliği
- Çoklu dil desteği

### 👑 Admin Paneli
- Kullanıcı yönetimi
- İstatistikler ve analitik
- Bot ayarları
- Sistem durumu

### 📊 İstatistikler
- Gerçek zamanlı bot istatistikleri
- Kullanıcı aktivite takibi
- İndirme sayıları
- Performans metrikleri

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- FFmpeg
- Telegram Bot Token
- Telegram API ID & Hash

### 1. Repository'yi klonlayın
```bash
git clone https://github.com/yourusername/kosemtra-bot.git
cd kosemtra-bot
```

### 2. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 3. FFmpeg'i yükleyin
- **Windows**: [FFmpeg indir](https://ffmpeg.org/download.html)
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

### 4. Konfigürasyon
`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
BOT_OWNER_ID=your_telegram_user_id_here
```

### 5. Botu çalıştırın
```bash
python main.py
```

## 🔧 API Bilgilerini Alma

### Telegram API Bilgileri
1. [my.telegram.org](https://my.telegram.org) adresine gidin
2. Telegram hesabınızla giriş yapın
3. "API development tools" bölümüne gidin
4. Yeni bir uygulama oluşturun
5. API ID ve API Hash'i alın

### Bot Token
1. [@BotFather](https://t.me/BotFather) ile konuşun
2. `/newbot` komutunu kullanın
3. Bot adını ve kullanıcı adını belirleyin
4. Bot token'ını alın

### Kullanıcı ID
1. [@userinfobot](https://t.me/userinfobot) ile konuşun
2. Telegram kullanıcı ID'nizi alın

## 🌐 Deployment

### Render.com (Önerilen)
1. GitHub repository'nizi Render.com'a bağlayın
2. Environment variables'ları ayarlayın
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`

#### Environment Variables:
```
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
BOT_OWNER_ID=your_telegram_user_id_here
RENDER_EXTERNAL_URL=https://your-bot-name.onrender.com
```

#### Keep-Alive Sistemi:
Bot otomatik olarak her 10 dakikada bir kendi URL'sine istek göndererek uykuya geçmesini engeller.

### Heroku
1. Heroku CLI'yi yükleyin
2. `Procfile` oluşturun: `web: python main.py`
3. Environment variables'ları ayarlayın
4. Deploy edin

### VPS/Server
1. Sunucunuza Python 3.8+ yükleyin
2. FFmpeg'i yükleyin
3. Repository'yi klonlayın
4. Bağımlılıkları yükleyin
5. Systemd service oluşturun

## 📱 Kullanım

### Temel Komutlar
- `/start` - Botu başlat
- `/help` - Yardım menüsü
- `/stats` - Bot istatistikleri

### Video İndirme
1. Video linkini gönderin
2. Format seçin (MP3/MP4)
3. Kalite seçin
4. İndirin!

### Hızlı İndirme
```
fast:https://youtu.be/VIDEO_ID
hızlı:https://youtu.be/VIDEO_ID
quick:https://youtu.be/VIDEO_ID
```

## 🛠️ Geliştirme

### Proje Yapısı
```
kosemtra-bot/
├── main.py              # Ana bot dosyası
├── config.py            # Konfigürasyon
├── admin_panel.py       # Admin paneli
├── advanced_features.py # Gelişmiş özellikler
├── virtual_keyboard.py  # Sanal klavye
├── requirements.txt     # Python bağımlılıkları
├── .env.example        # Örnek environment dosyası
└── README.md           # Bu dosya
```

### Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Destek

- **Issues**: [GitHub Issues](https://github.com/yourusername/kosemtra-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/kosemtra-bot/discussions)
- **Telegram**: [@yourusername](https://t.me/yourusername)

## 🙏 Teşekkürler

- [Pyrogram](https://pyrogram.org) - Telegram API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video indirme
- [FFmpeg](https://ffmpeg.org) - Video/audio işleme

## 📊 İstatistikler

![GitHub stars](https://img.shields.io/github/stars/yourusername/kosemtra-bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/kosemtra-bot?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/kosemtra-bot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/kosemtra-bot)

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!