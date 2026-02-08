import React, { useState } from 'react';
import axios from 'axios';
import { Download, Youtube, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

function App() {
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('1080');
  const [status, setStatus] = useState('idle'); 
  const [errorMsg, setErrorMsg] = useState('');

  const handleDownload = async () => {
    if (!url || status === 'loading') return;
    
    setStatus('loading');
    setErrorMsg(''); // Yeni istekte eski hatayı temizle
    
    try {
        const response = await axios.post('https://yt-video-downloader-production.up.railway.app/download', {
            url: url,
            quality: quality
        }, { 
            responseType: 'blob',
            timeout: 0, // Sınırsız bekleme
        });

        const blob = new Blob([response.data], { type: 'video/mp4' });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', `video_${quality}p.mp4`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl); // Bellek temizliği
        
        setStatus('success');
    } catch (err) {
        console.error("Hata detayı:", err);
        // Hata mesajını daha detaylı yakalıyoruz
        if (err.response) {
            setErrorMsg(`Sunucu Hatası: ${err.response.status}`);
        } else if (err.request) {
            setErrorMsg("Sunucuya ulaşılamıyor (CORS veya Network hatası)");
        } else {
            setErrorMsg(err.message);
        }
        setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-slate-800 rounded-2xl shadow-2xl p-8 border border-slate-700">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <Youtube className="text-red-500 w-10 h-10" />
          <h1 className="text-3xl font-bold tracking-tight">YT Downloader</h1>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">YouTube Video URL</label>
            <input 
              type="text" 
              placeholder="https://www.youtube.com/watch?v=..." 
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-red-500 outline-none transition-all"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-slate-400 mb-2">Kalite</label>
              <select 
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 outline-none"
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
              >
                <option value="1080">1080p Full HD</option>
                <option value="720">720p HD</option>
                <option value="480">480p SD</option>
              </select>
            </div>
          </div>

          <button 
            onClick={handleDownload}
            disabled={status === 'loading' || !url}
            className={`w-full py-4 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${
              status === 'loading' ? 'bg-slate-700 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700 active:scale-95'
            }`}
          >
            {status === 'loading' ? (
              <><Loader2 className="animate-spin" /> İşleniyor (Bekleyin)...</>
            ) : (
              <><Download /> Videoyu İndir</>
            )}
          </button>

          {status === 'success' && (
            <div className="flex items-center gap-2 text-green-400 justify-center bg-green-400/10 py-3 rounded-lg border border-green-400/20">
              <CheckCircle size={20} /> İndirme Başladı!
            </div>
          )}
          
          {status === 'error' && (
            <div className="flex items-center gap-2 text-red-400 justify-center bg-red-400/10 py-3 rounded-lg border border-red-400/20">
              <AlertCircle size={20} /> {errorMsg}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;