from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from veritabani import Oturum, Itiraf
from datetime import datetime
import time

app = FastAPI()
sablonlar = Jinja2Templates(directory="sablonlar")

# IP'leri ve son atılma zamanlarını tutacağımız sözlük
IP_KAYITLARI = {}
BEKLEME_SURESI = 60 # 60 saniye

@app.get("/", response_class=HTMLResponse)
def ana_sayfa(istek: Request):
    db = Oturum()
    tum_itiraflar = db.query(Itiraf).order_by(Itiraf.id.desc()).all()
    db.close()

    return sablonlar.TemplateResponse("index.html", {"request": istek, "itiraflar":tum_itiraflar})

@app.post("/itiraf-et")
def itiraf_et(istek: Request, mesaj: str = Form(...)):
    kullanici_ip = istek.client.host
    su_anki_zaman = time.time()
    
    # --- RATE LIMITING (KORUMA KALKANI) ---
    if kullanici_ip in IP_KAYITLARI:
        gecen_sure = su_anki_zaman - IP_KAYITLARI[kullanici_ip]
        if gecen_sure < BEKLEME_SURESI:
            # Hata fırlatmak (JSON) yerine sayfayı hata değişkeniyle tekrar yüklüyoruz
            db = Oturum()
            tum_itiraflar = db.query(Itiraf).order_by(Itiraf.id.desc()).all()
            db.close()
            return sablonlar.TemplateResponse("index.html", {
                "request": istek, 
                "itiraflar": tum_itiraflar, 
                "hata": "Çok hızlı itiraf gönderiyorsunuz! Lütfen 1 dakika bekleyin."
            })
            
    # Eğer spam yapmıyorsa süresini güncelle
    IP_KAYITLARI[kullanici_ip] = su_anki_zaman
    # -------------------------------------

    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db = Oturum()

    yeni_itiraf = Itiraf(mesaj=mesaj, ip_adresi=kullanici_ip, tarih=su_an)
    db.add(yeni_itiraf)
    db.commit()
    db.close()

    return RedirectResponse(url="/", status_code=303)
 