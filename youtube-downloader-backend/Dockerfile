# Python 3.10 Slim versiyonu (Hafif ve hızlı)
FROM python:3.10-slim

# Çalışma klasörü
WORKDIR /app

# 1. SİSTEM GÜNCELLEMELERİ (Full Paket)
# ffmpeg: Video birleştirme için
# nodejs: YouTube şifrelerini çözmek için
# git: En güncel yt-dlp sürümünü çekmek için
# curl: Lazım olur diye
RUN apt-get update && \
    apt-get install -y ffmpeg nodejs git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Gereksinimleri kopyala
COPY requirements.txt .

# 3. Kütüphaneleri kur (Önbelleği temizleyerek)
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

# 4. Uygulama dosyalarını kopyala
COPY . .

# 5. Portu aç
EXPOSE 5000

# 6. Başlat
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]