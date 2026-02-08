import uuid
import os
import io
from flask import Flask, request, send_file, after_this_request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '1080')
    
    unique_id = str(uuid.uuid4())[:8]
    base_name = f"video_{unique_id}"
    final_file_path = f"{base_name}.mp4"
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': f"{base_name}.%(ext)s", 
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Dosya ismini doğrula
        if not os.path.exists(final_file_path):
            files = [f for f in os.listdir('.') if f.startswith(base_name) and f.endswith('.mp4')]
            if files: final_file_path = files[0]
            else: return {"error": "Dosya bulunamadı"}, 500

        # --- ÇÖZÜM: Dosyayı Belleğe Alma ---
        # Dosyayı RAM'e okuyoruz, böylece diskteki dosya serbest kalıyor.
        return_data = io.BytesIO()
        with open(final_file_path, 'rb') as f:
            return_data.write(f.read())
        return_data.seek(0) # Okuma imlecini başa sar

        # Diskten hemen silebiliriz çünkü artık veri RAM'de
        os.remove(final_file_path)
        print(f"--- Temizlik Başarılı: {final_file_path} diskten silindi (RAM'den gönderiliyor) ---")

        return send_file(
            return_data,
            as_attachment=True,
            download_name=f"video_{quality}p.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        print(f"HATA: {str(e)}")
        # Hata durumunda kalmış olabilecek dosyayı temizle
        if 'final_file_path' in locals() and os.path.exists(final_file_path):
            os.remove(final_file_path)
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)