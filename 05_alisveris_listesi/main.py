from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from veritabani import Oturum, Urun
import json

app = FastAPI()
sablonlar = Jinja2Templates(directory="sablonlar")

# Dışarıdan gelecek verinin kalıbı (Pydantic)
class YeniUrunIstegi(BaseModel):
    urun_adi: str

class MiktarGuncelleme(BaseModel):
    islem: str # "artir" veya "azalt"

# Sadece ana HTML sayfasını gösteren boş rota
@app.get("/", response_class=HTMLResponse)
def ana_sayfa(istek: Request):
    return sablonlar.TemplateResponse("index.html", {"request": istek})

# Bütün ürünleri JSON olarak fırlatan API rotası
@app.get("/urunler")
def urunleri_getir():
    db = Oturum()
    tum_urunler = db.query(Urun).all()
    db.close()
    return tum_urunler

# Kataloğu (JSON) Dışarıya Sunan API
@app.get("/katalog")
def katalog_getir():
    with open("katalog.json", "r", encoding="utf-8") as f:
        katalog = json.load(f)
    return katalog

# Dışarıdan gelen veriyi alıp JSON fırlatan API rotası (Miktar Kontrollü)
@app.post("/urun-ekle")
def urun_ekle(istek: YeniUrunIstegi):
    db = Oturum()
    mevcut_urun = db.query(Urun).filter(Urun.urun_adi == istek.urun_adi).first()
    
    if mevcut_urun:
        mevcut_urun.miktar += 1
        db.commit()
        db.refresh(mevcut_urun)
        sonuc = mevcut_urun
    else:
        yeni = Urun(urun_adi=istek.urun_adi, miktar=1)
        db.add(yeni)
        db.commit()
        db.refresh(yeni)
        sonuc = yeni
        
    db.close()
    return sonuc

# Ürünü Veritabanından Silen API Rotası
@app.delete("/urun-sil/{urun_id}")
def urun_sil(urun_id: int):
    db = Oturum()
    silinecek = db.query(Urun).filter(Urun.id == urun_id).first()
    if silinecek:
        db.delete(silinecek)
        db.commit()
    db.close()
    return {"mesaj": "Ürün başarıyla silindi!"}

# Ürünün 'Alındı' Durumunu Tersine Çeviren API Rotası
@app.put("/urun-guncelle/{urun_id}")
def urun_guncelle(urun_id: int):
    db = Oturum()
    guncellenecek = db.query(Urun).filter(Urun.id == urun_id).first()
    if guncellenecek:
        # Eski değer True ise False, False ise True yapar
        guncellenecek.alindi_mi = not guncellenecek.alindi_mi 
        db.commit()
        db.refresh(guncellenecek)
    db.close()
    return guncellenecek

# Miktarı Arttıran veya Azaltan (Sıfırsa Silen) Rota
@app.put("/miktar-guncelle/{urun_id}")
def miktar_guncelle(urun_id: int, istek: MiktarGuncelleme):
    db = Oturum()
    urun = db.query(Urun).filter(Urun.id == urun_id).first()
    if urun:
        if istek.islem == "artir":
            urun.miktar += 1
        elif istek.islem == "azalt":
            urun.miktar -= 1
            
        if urun.miktar <= 0:
            db.delete(urun)
            db.commit()
            db.close()
            return {"durum": "silindi"}
        else:
            db.commit()
            db.refresh(urun)
            db.close()
            return urun
    db.close()
    return {"durum": "bulunamadi"}