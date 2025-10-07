# Python 3.11 slim image kullan
FROM python:3.11-slim

# Sistem paketlerini güncelle ve FFmpeg yükle
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# FFmpeg versiyonunu kontrol et
RUN ffmpeg -version

# Çalışma dizinini ayarla
WORKDIR /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Gerekli dizinleri oluştur
RUN mkdir -p /tmp/downloads /tmp/temp

# Port'u expose et
EXPOSE 10000

# Uygulamayı çalıştır
CMD ["python", "main.py"]
