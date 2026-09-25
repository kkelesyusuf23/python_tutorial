import json
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from sqlalchemy.orm import Session
from veritabani import SessionLocal, Anket, Oy

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Veritabanı oturumunu yöneten Dependency fonksiyonu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def anasayfa(request: Request, db: Session = Depends(get_db)):
    anketler = db.query(Anket).all()
    return templates.TemplateResponse("index.html", {"request": request, "anketler": anketler})

@app.post("/anket-olustur")
def anket_olustur(
    baslik: str = Form(...),
    sorular_json: str = Form(...), # Javascript bu sütunu doldurup bize gönderecek
    db: Session = Depends(get_db)
):
    # Javascript'in yolladığı metin (string) halindeki JSON'ı Python Listesine (Dict) çeviriyoruz
    sorular_listesi = json.loads(sorular_json)
    
    yeni_anket = Anket(baslik=baslik, sorular=sorular_listesi)
    db.add(yeni_anket)
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/anket/{anket_id}", response_class=HTMLResponse)
def anket_coz(request: Request, anket_id: int, db: Session = Depends(get_db)):
    anket = db.query(Anket).filter(Anket.id == anket_id).first()
    return templates.TemplateResponse("coz.html", {"request": request, "anket": anket})

@app.post("/anket/{anket_id}/oy-ver")
async def oy_ver(request: Request, anket_id: int, db: Session = Depends(get_db)):
    # Kullanıcı HTML formundan (A, B, C gibi) hangi seçenekleri işaretlediyse hepsini yakala
    form_data = await request.form()
    
    cevaplar = {}
    for key, value in form_data.items():
        if key.startswith("soru_"):
            # Örn: 'soru_0' -> '0'
            soru_index = key.split("_")[1]
            cevaplar[soru_index] = value
            
    # Hangi soruya (index) hangi cevabın verildiğini JSON olarak veritabanına kaydet
    yeni_oy = Oy(anket_id=anket_id, cevaplar=cevaplar)
    db.add(yeni_oy)
    db.commit()
    
    # Oy verdikten sonra sonuçlar sayfasına yönlendir
    return RedirectResponse(url=f"/anket/{anket_id}/sonuclar", status_code=303)

@app.get("/anket/{anket_id}/sonuclar", response_class=HTMLResponse)
def sonuclar(request: Request, anket_id: int, db: Session = Depends(get_db)):
    anket = db.query(Anket).filter(Anket.id == anket_id).first()
    oylar = db.query(Oy).filter(Oy.anket_id == anket_id).all()
    
    # İstatistik algoritması: Her soru ve seçenek için sayaçları sıfırla
    istatistik = {}
    for i, soru in enumerate(anket.sorular):
        # Örn: {"Mavi": 0, "Kırmızı": 0}
        istatistik[str(i)] = {secenek: 0 for secenek in soru["secenekler"]}
        
    # Veritabanındaki tüm oyları tek tek say
    for oy in oylar:
        for soru_idx, secilen_cevap in oy.cevaplar.items():
            if soru_idx in istatistik and secilen_cevap in istatistik[soru_idx]:
                istatistik[soru_idx][secilen_cevap] += 1
                
    return templates.TemplateResponse("sonuclar.html", {
        "request": request, 
        "anket": anket, 
        "istatistik": istatistik,
        "toplam_oy": len(oylar)
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 