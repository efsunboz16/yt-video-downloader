# 1. Python 3.10 tabanlı hafif Linux
FROM python:3.10-slim

# 2. Çalışma dizini
WORKDIR /app

# 3. SİSTEM GÜNCELLEMELERİ - BURASI KRİTİK!
# Hem ffmpeg (birleştirme için) hem nodejs (YouTube şifresi çözmek için) kuruyoruz.
# curl da ekledim ne olur ne olmaz.
RUN apt-get update && \
    apt-get install -y ffmpeg nodejs curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Gereksinimleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Dosyaları kopyala
COPY . .

# 6. Portu aç
EXPOSE 5000

# 7. Başlat
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]