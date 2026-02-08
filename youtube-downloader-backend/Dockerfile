# 1. Python 3.10 tabanlı hafif bir Linux sürümü kullan
FROM python:3.10-slim

# 2. Çalışma dizinini ayarla
WORKDIR /app

# 3. Sistem güncellemelerini yap ve FFmpeg'i kur (Kritik Adım)
# Ayrıca Node.js ekliyoruz ki loglardaki o sarı JS uyarısı da gitsin.
RUN apt-get update && \
    apt-get install -y ffmpeg nodejs && \
    rm -rf /var/lib/apt/lists/*

# 4. Önce sadece gereksinimleri kopyala ve kur (Cache avantajı için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kalan tüm proje dosyalarını kopyala
COPY . .

# 6. Uygulamanın çalışacağı portu belirt
EXPOSE 5000

# 7. Uygulamayı başlat
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]