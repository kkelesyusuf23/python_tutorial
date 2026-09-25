from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

# Yazdığımız veritabani dosyasındaki objeleri içe aktarıyoruz
from veritabani import engine, Base, SessionLocal, get_db, Kullanici, Oda, Rezervasyon

# SQLAlchemy ile SQLite veritabanı dosyasını ve tablolarını fiziki olarak oluşturuyoruz
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# BAŞLANGIÇ VERİSİ EKLEME (SEEDING)
# ==========================================
# Uygulama ilk açıldığında veritabanı bomboş olacağı için, 
# formda seçebileceğimiz birkaç müşteri ve oda ekliyoruz.
def ornek_veri_ekle():
    db = SessionLocal()
    # Eğer sistemde hiç kullanıcı yoksa, başlangıç verilerini ekle
    if db.query(Kullanici).count() == 0:
        db.add(Kullanici(ad_soyad="Yusuf Keleş", eposta="yusuf@mail.com"))
        db.add(Kullanici(ad_soyad="Ahmet Yılmaz", eposta="ahmet@mail.com"))
        
        db.add(Oda(oda_numarasi="101 (Standart)", fiyat=1500.0))
        db.add(Oda(oda_numarasi="102 (Manzaralı)", fiyat=2500.0))
        db.add(Oda(oda_numarasi="201 (Kral Dairesi)", fiyat=5000.0))
        
        db.commit()
    db.close()

# Sunucu başlarken fonksiyonu çağır
ornek_veri_ekle()


# ==========================================
# ANA SAYFA ROTASI (VERİLERİ ÇEKME)
# ==========================================
@app.get("/", response_class=HTMLResponse)
def ana_sayfa(request: Request, db: Session = Depends(get_db)):
    # 1. Tablodaki tüm kullanıcıları çek
    kullanicilar = db.query(Kullanici).all()
    # 2. Tablodaki tüm odaları çek
    odalar = db.query(Oda).all()
    # 3. Tüm rezervasyonları çek (SİHİR BURADA)
    # SQLAlchemy relationship köprüsü sayesinde, Rezervasyonları çekerken 
    # arka planda bağlı olduğu Kullanıcı ve Oda verilerini de otomatik olarak getirir.
    rezervasyonlar = db.query(Rezervasyon).all() 
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "odalar": odalar, 
        "kullanicilar": kullanicilar,
        "rezervasyonlar": rezervasyonlar
    })


# ==========================================
# REZERVASYON KAYDETME ROTASI (VERİ YAZMA)
# ==========================================
@app.post("/rezervasyon-yap")
def rezervasyon_kaydet(
    kullanici_id: int = Form(...),
    oda_id: int = Form(...),
    giris_tarihi: str = Form(...),
    cikis_tarihi: str = Form(...),
    db: Session = Depends(get_db)
):
    # Formdan gelen ID numaralarını kullanarak köprü (Rezervasyon) tablosuna yeni kayıt ekliyoruz
    yeni_rezervasyon = Rezervasyon(
        kullanici_id=kullanici_id,
        oda_id=oda_id,
        giris_tarihi=giris_tarihi,
        cikis_tarihi=cikis_tarihi
    )
    
    db.add(yeni_rezervasyon)
    db.commit() # Veritabanına kaydet
    
    # İşlem bittikten sonra kullanıcıyı tekrar ana sayfaya (GET "/") yönlendiriyoruz (Sayfayı yeniliyoruz)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 