import uuid
import os
import io
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

COOKIE_FILE = "cookies.txt"

# Cookie dosyasını oluştur
if os.environ.get('YOUTUBE_COOKIES'):
    with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
        f.write(os.environ.get('YOUTUBE_COOKIES'))

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '1080')
    
    unique_id = str(uuid.uuid4())[:8]
    base_name = f"video_{unique_id}"
    final_file_path = os.path.abspath(f"{base_name}.mp4")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': f"{base_name}.%(ext)s",
        'noplaylist': True,
        'quiet': False,
        'overwrites': True,
        # Cookie dosyasını kullan (Android kodu YOK)
        'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not os.path.exists(final_file_path):
            files = [f for f in os.listdir('.') if f.startswith(base_name)]
            if files: final_file_path = os.path.abspath(files[0])
            else: raise Exception("Dosya indirilemedi.")

        return_data = io.BytesIO()
        with open(final_file_path, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)
        os.remove(final_file_path)

        return send_file(return_data, as_attachment=True, download_name=f"video_{unique_id}.mp4", mimetype='video/mp4')

    except Exception as e:
        print(f"HATA: {str(e)}")
        if os.path.exists(final_file_path): os.remove(final_file_path)
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))