import uuid
import os
import io
import time
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Cookie ayarları
COOKIE_FILE = "cookies.txt"

def setup_cookies():
    cookie_content = os.environ.get('YOUTUBE_COOKIES')
    if cookie_content:
        try:
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                f.write(cookie_content)
            print(f"--- Cookie dosyası hazırlandı ---")
        except Exception as e:
            print(f"--- Cookie hatası: {str(e)} ---")

setup_cookies()

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '1080')
    
    if not url: return {"error": "URL yok"}, 400
    
    unique_id = str(uuid.uuid4())[:8]
    base_name = f"video_{unique_id}"
    final_file_path = os.path.abspath(f"{base_name}.mp4")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': f"{base_name}.%(ext)s",
        'noplaylist': True,
        'quiet': False,
        'overwrites': True,
        
        # --- KRİTİK AYAR: MOBİL TAKLİDİ ---
        # YouTube'u Android uygulamasıymışız gibi kandırıyoruz.
        # Bu sayede JS Challenge ve Signature hatalarını atlıyoruz.
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        },
        # ----------------------------------

        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    # Cookie varsa ekle
    if os.path.exists(COOKIE_FILE):
        ydl_opts['cookiefile'] = COOKIE_FILE

    try:
        print(f"--- Android Client ile indiriliyor: {url} ---")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Dosya adı kontrolü (yt-dlp bazen uzantıyı değiştirebilir)
        if not os.path.exists(final_file_path):
            files = [f for f in os.listdir('.') if f.startswith(base_name)]
            if files: final_file_path = os.path.abspath(files[0])
            else: raise Exception("Dosya indirilemedi.")

        # RAM'e al
        return_data = io.BytesIO()
        with open(final_file_path, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)

        # Temizlik
        os.remove(final_file_path)

        return send_file(
            return_data,
            as_attachment=True,
            download_name=f"video_{unique_id}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        print(f"HATA: {str(e)}")
        if os.path.exists(final_file_path): os.remove(final_file_path)
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)