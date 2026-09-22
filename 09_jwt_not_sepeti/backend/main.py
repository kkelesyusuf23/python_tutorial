from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from veritabani import SessionLocal, Kullanici, Not, sifre_hashle, sifre_dogrula
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="../frontend")

# JWT AYARLARI (Güvenlik Anahtarı)
SECRET_KEY = "benim_cok_gizli_anahtarim"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Biletin (Token) 1 saatlik ömrü var

# FastAPI'nin JWT Token'ı nerede arayacağını belirtiyoruz (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="giris")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# JWT YARDIMCI FONKSİYONLARI
# ---------------------------------------------------------

def token_olustur(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Sözlüğü, gizli anahtarımızla şifreliyoruz
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Bu fonksiyon her "Korumalı (Protected)" rotadan önce çalışır
# Gelen Token'ı kontrol eder, geçersizse reddeder, geçerliyse kullanıcıyı döndürür.
def aktif_kullanici_getir(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        kullanici_adi: str = payload.get("sub")
        if kullanici_adi is None:
            raise HTTPException(status_code=401, detail="Yetkisiz erişim")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş token")
        
    kullanici = db.query(Kullanici).filter(Kullanici.kullanici_adi == kullanici_adi).first()
    if kullanici is None:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return kullanici

# ---------------------------------------------------------
# API ROTALARI
# ---------------------------------------------------------

class KayitVerisi(BaseModel):
    kullanici_adi: str
    sifre: str

class NotVerisi(BaseModel):
    baslik: str
    icerik: str

# 0. ARAYÜZ (HTML)
@app.get("/")
def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 1. HERKESE AÇIK: Kayıt Ol
@app.post("/kayit")
def kayit_ol(veri: KayitVerisi, db: Session = Depends(get_db)):
    var_mi = db.query(Kullanici).filter(Kullanici.kullanici_adi == veri.kullanici_adi).first()
    if var_mi:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış!")
        
    yeni_kullanici = Kullanici(
        kullanici_adi=veri.kullanici_adi,
        sifre_hash=sifre_hashle(veri.sifre)
    )
    db.add(yeni_kullanici)
    db.commit()
    return {"mesaj": "Kayıt başarılı"}

# 2. HERKESE AÇIK: Giriş Yap (Token Üretimi)
@app.post("/giris")
def giris_yap(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    kullanici = db.query(Kullanici).filter(Kullanici.kullanici_adi == form_data.username).first()
    
    if not kullanici or not sifre_dogrula(form_data.password, kullanici.sifre_hash):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")
        
    # Kullanıcı doğru bilgilerle geldi, ona 1 saatlik biletini verelim
    token = token_olustur({"sub": kullanici.kullanici_adi})
    return {"access_token": token, "token_type": "bearer"}

# 3. KORUMALI ROTA: Notları Getir (Sadece Token'ı olanlar girebilir)
@app.get("/notlar")
def notlari_getir(aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir), db: Session = Depends(get_db)):
    # Sadece istek atan kişiye (aktif_kullanici) ait notları filtrele
    notlar = db.query(Not).filter(Not.kullanici_id == aktif_kullanici.id).all()
    return [{"id": n.id, "baslik": n.baslik, "icerik": n.icerik} for n in notlar]

# 4. KORUMALI ROTA: Not Ekle
@app.post("/notlar")
def not_ekle(veri: NotVerisi, aktif_kullanici: Kullanici = Depends(aktif_kullanici_getir), db: Session = Depends(get_db)):
    yeni_not = Not(baslik=veri.baslik, icerik=veri.icerik, kullanici_id=aktif_kullanici.id)
    db.add(yeni_not)
    db.commit()
    return {"mesaj": "Not eklendi"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
