# Python 3.11 slim image kullan
FROM python:3.11-slim

# Sistem paketlerini güncelle ve FFmpeg yükle
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Gerekli dizinleri oluştur
RUN mkdir -p downloads temp

# Port'u expose et
EXPOSE 5000

# Uygulamayı çalıştır
CMD ["python", "main.py"]
