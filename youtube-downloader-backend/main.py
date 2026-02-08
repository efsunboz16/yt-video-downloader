import uuid
import os
import io
import time
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# CORS ayarları: Frontend'den gelen isteklere izin ver
CORS(app, resources={r"/*": {"origins": "*"}})

# --- COOKIE AYARLARI (KRİTİK BÖLÜM) ---
COOKIE_FILE = "cookies.txt"

def setup_cookies():
    """Railway ortam değişkeninden cookie'yi alıp dosyaya yazar."""
    cookie_content = os.environ.get('YOUTUBE_COOKIES')
    if cookie_content:
        try:
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                f.write(cookie_content)
            print(f"--- BAŞARILI: Cookie dosyası oluşturuldu ({len(cookie_content)} karakter) ---")
            return True
        except Exception as e:
            print(f"--- HATA: Cookie dosyası yazılamadı: {str(e)} ---")
            return False
    else:
        print("--- UYARI: 'YOUTUBE_COOKIES' değişkeni bulunamadı! Bot korumasına takılabilirsin. ---")
        return False

# Uygulama başlarken cookie dosyasını hazırla
setup_cookies()

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '1080')
    
    if not url:
        return {"error": "URL gerekli"}, 400
    
    unique_id = str(uuid.uuid4())[:8]
    base_name = f"video_{unique_id}"
    final_file_path = os.path.abspath(f"{base_name}.mp4")
    
    # yt-dlp Ayarları
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': f"{base_name}.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
        'quiet': False,
        # Dosya üzerine yazma izni
        'overwrites': True,
    }

    # Eğer cookie dosyası oluştuysa, yt-dlp'ye bu dosyayı kullanmasını söyle
    if os.path.exists(COOKIE_FILE):
        ydl_opts['cookiefile'] = COOKIE_FILE
        print("--- Bilgi: İndirme işleminde Cookie kullanılıyor ---")

    try:
        print(f"--- İndirme Başlıyor: {url} ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Dosya kontrolü (Bazen uzantı farklı olabilir, kontrol edelim)
        if not os.path.exists(final_file_path):
            # Belki .mkv veya .webm indi, klasörü tarayalım
            files = [f for f in os.listdir('.') if f.startswith(base_name)]
            if files:
                final_file_path = os.path.abspath(files[0])
            else:
                return {"error": "Video indirildi ama dosya bulunamadı."}, 500

        # --- DOSYAYI BELLEĞE (RAM) AL ---
        return_data = io.BytesIO()
        with open(final_file_path, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)

        # --- TEMİZLİK ---
        # Disk dolu hatası almamak için hemen siliyoruz
        os.remove(final_file_path)
        print(f"--- Temizlik: {final_file_path} silindi. Video gönderiliyor. ---")

        return send_file(
            return_data,
            as_attachment=True,
            download_name=f"video_{unique_id}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        error_msg = str(e)
        print(f"--- KRİTİK HATA: {error_msg} ---")
        
        # Hata durumunda kalan dosyaları temizle
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
            
        # Kullanıcıya anlamlı hata dön
        if "Sign in" in error_msg:
            return {"error": "YouTube Bot Koruması: Lütfen Cookie'lerinizi güncelleyin."}, 403
        
        return {"error": f"Sunucu Hatası: {error_msg}"}, 500

if __name__ == '__main__':
    # Railway PORT değişkenini dinler
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)