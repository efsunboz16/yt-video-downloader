import uuid
import os
import io
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# CORS ayarını tüm kaynaklara izin verecek şekilde genişlettik
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '1080')
    
    if not url:
        return {"error": "URL gerekli"}, 400
    
    unique_id = str(uuid.uuid4())[:8]
    base_name = f"video_{unique_id}"
    # Sunucu içinde dosya yollarını garantiye almak için mutlak yol kullanıyoruz
    final_file_path = os.path.abspath(f"{base_name}.mp4")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': f"{base_name}.%(ext)s", 
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Dosyanın oluşup oluşmadığını kontrol et
        if not os.path.exists(final_file_path):
            files = [f for f in os.listdir('.') if f.startswith(base_name) and f.endswith('.mp4')]
            if files:
                final_file_path = os.path.abspath(files[0])
            else:
                return {"error": "Video işlenemedi (FFmpeg hatası olabilir)"}, 500

        # Belleğe alma işlemi (Windows ve Linux kilitlenmelerini önler)
        return_data = io.BytesIO()
        with open(final_file_path, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0)

        # Temizlik
        os.remove(final_file_path)
        print(f"--- Başarılı: {final_file_path} silindi ve gönderiliyor ---")

        return send_file(
            return_data,
            as_attachment=True,
            download_name=f"video_{quality}p.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        print(f"HATA: {str(e)}")
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
        return {"error": str(e)}, 500

if __name__ == '__main__':
    # Railway gibi platformlar için PORT değişkenini dinamik alabiliriz
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)