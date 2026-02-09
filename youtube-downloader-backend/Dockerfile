FROM python:3.10-slim

WORKDIR /app

# Node.js (v18) ve FFmpeg kurulumu - KESİN ÇÖZÜM
RUN apt-get update && \
    apt-get install -y curl ffmpeg git && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# pip güncelle ve gereksinimleri kur
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]