from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import yt_dlp
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# İndirilen videoların tutulacağı klasör
os.makedirs("gecici_videolar", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/indir")
def video_indir(link: str = Form(...)):
    # yt-dlp ayarları: En iyi kaliteyi seç ve dosyayı gecici_videolar içine kaydet
    ydl_opts = {
        'outtmpl': 'gecici_videolar/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': False
    }
    
    # Kütüphaneyi çalıştırıyoruz
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Önce videonun bilgilerini (ismini, uzunluğunu) çek
        info_dict = ydl.extract_info(link, download=True)
        # Videonun diske kaydedildiği tam konumu al (Örn: gecici_videolar/Python_Dersi.mp4)
        dosya_yolu = ydl.prepare_filename(info_dict)
        
    # Python dosyayı indirmeyi bitirdiğinde FileResponse ile bunu tarayıcıya (Download'a) iletiyoruz!
    dosya_adi = os.path.basename(dosya_yolu)
    return FileResponse(dosya_yolu, media_type="video/mp4", filename=dosya_adi)
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
