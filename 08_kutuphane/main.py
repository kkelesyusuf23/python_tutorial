from fastapi import FastAPI, Form, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from veritabani import SessionLocal, Yazar, Kitap

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Veritabanı Oturumu (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. ARAYÜZ (HTML) ROTALARI
@app.get("/", response_class=HTMLResponse)
def ana_sayfa(request: Request, db: Session = Depends(get_db)):
    # Tüm yazarları (ilişkili kitaplarıyla birlikte) çek
    yazarlar = db.query(Yazar).all()
    return templates.TemplateResponse("index.html", {"request": request, "yazarlar": yazarlar})

@app.post("/yazar_ekle")
def yazar_ekle(isim: str = Form(...), ulke: str = Form(...), db: Session = Depends(get_db)):
    yeni_yazar = Yazar(isim=isim, ulke=ulke)
    db.add(yeni_yazar)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/kitap_ekle")
def kitap_ekle(baslik: str = Form(...), sayfa_sayisi: int = Form(...), yazar_id: int = Form(...), db: Session = Depends(get_db)):
    # Yeni bir kitap oluşturuyoruz ve seçilen yazar_id ile onu o yazara kilitliyoruz.
    yeni_kitap = Kitap(baslik=baslik, sayfa_sayisi=sayfa_sayisi, yazar_id=yazar_id)
    db.add(yeni_kitap)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# 2. RESTful JSON API ROTALARI
# Sadece veri döner, HTML barındırmaz. (Mobil uygulamaların veriyi çektiği yer)
@app.get("/api/yazarlar")
def api_yazarlar(db: Session = Depends(get_db)):
    yazarlar = db.query(Yazar).all()
    sonuc = []
    
    # SQLAlchemy objelerini saf Python sözlüğüne (Dictionary) çeviriyoruz
    for y in yazarlar:
        sonuc.append({
            "id": y.id,
            "isim": y.isim,
            "ulke": y.ulke,
            "kitap_sayisi": len(y.kitaplar),
            # Yazarın kitaplarını da içine dizi olarak koyuyoruz
            "kitaplar": [{"baslik": k.baslik, "sayfa": k.sayfa_sayisi} for k in y.kitaplar]
        })
        
    return sonuc

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
