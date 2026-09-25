from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mutagen
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Ses dosyalarını ve içlerinden çıkarılan kapakları dışarı (HTML'e) açıyoruz
os.makedirs("sesler", exist_ok=True)
os.makedirs("kapaklar", exist_ok=True)
app.mount("/sesler", StaticFiles(directory="sesler"), name="sesler")
app.mount("/kapaklar", StaticFiles(directory="kapaklar"), name="kapaklar")

@app.get("/", response_class=HTMLResponse)
def podcast_ana_sayfa(request: Request):
    podcast_listesi = []
    ses_klasoru = "sesler"
    
    # 'sesler' klasöründeki tüm MP3 dosyalarını tara
    for dosya_adi in os.listdir(ses_klasoru):
        if not dosya_adi.endswith(".mp3"):
            continue
            
        dosya_yolu = os.path.join(ses_klasoru, dosya_adi)
        
        try:
            # 1. Mutagen ile MP3 dosyasının genetiğini (Meta Verilerini) okuyoruz
            ses_dosyasi = mutagen.File(dosya_yolu)
            
            # 2. Şarkı Adı (TIT2) ve Sanatçı (TPE1) bilgilerini çekiyoruz
            # Eğer dosyada bilgi yoksa, varsayılan olarak dosya adını basıyoruz
            baslik = str(ses_dosyasi.tags.get("TIT2", dosya_adi)) if ses_dosyasi.tags and "TIT2" in ses_dosyasi.tags else dosya_adi
            sanatci = str(ses_dosyasi.tags.get("TPE1", "Bilinmeyen Sanatçı")) if ses_dosyasi.tags and "TPE1" in ses_dosyasi.tags else "Bilinmeyen Sanatçı"
            
            # 3. Süreyi saniye olarak çekip Dakika:Saniye formatına çeviriyoruz
            saniye = int(ses_dosyasi.info.length)
            dakika = saniye // 60
            kalan_saniye = saniye % 60
            sure_str = f"{dakika}:{kalan_saniye:02d}"
            
            # 4. Dosyanın içine gömülü (embedded) Albüm Kapağı resmi var mı diye bakıyoruz
            kapak_url = None
            if ses_dosyasi.tags:
                for tag in ses_dosyasi.tags.values():
                    # APIC, MP3 dosyalarındaki resim çerçevesinin standart adıdır
                    if tag.FrameID == 'APIC':
                        # Resmi söküp 'kapaklar' klasörüne gerçek bir JPG dosyası olarak kaydediyoruz!
                        kapak_dosya_adi = f"{dosya_adi}_kapak.jpg"
                        kapak_yolu = os.path.join("kapaklar", kapak_dosya_adi)
                        with open(kapak_yolu, "wb") as img:
                            img.write(tag.data)
                        kapak_url = f"/kapaklar/{kapak_dosya_adi}"
                        break
            
            # Eğer dosyanın içine gömülü resim yoksa internetten varsayılan bir ikon koy
            if not kapak_url:
                kapak_url = "https://cdn-icons-png.flaticon.com/512/860/860142.png"
                
            podcast_listesi.append({
                "dosya_adi": dosya_adi,
                "baslik": baslik,
                "sanatci": sanatci,
                "sure": sure_str,
                "kapak_url": kapak_url,
                "dosya_url": f"/sesler/{dosya_adi}"
            })
            
        except Exception as e:
            print(f"Hata oluştu ({dosya_adi}): {e}")
            
    return templates.TemplateResponse("index.html", {"request": request, "podcastler": podcast_listesi})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 