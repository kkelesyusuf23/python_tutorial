from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from veritabani import Oturum, Link
import random
import string

app = FastAPI()
sablonlar = Jinja2Templates(directory="sablonlar")

# Eşsiz kısa kod üretici algoritma (Örn: xY7z9)
def kisa_kod_uret(uzunluk=5):
    karakterler = string.ascii_letters + string.digits
    return ''.join(random.choices(karakterler, k=uzunluk))

@app.get("/", response_class=HTMLResponse)
def ana_sayfa(istek: Request):
    db = Oturum()
    # En son kısaltılan linkler en üstte çıksın
    tum_linkler = db.query(Link).order_by(Link.id.desc()).all()
    db.close()
    return sablonlar.TemplateResponse("index.html", {"request": istek, "linkler": tum_linkler})

@app.post("/kisalt")
def link_kisalt(istek: Request, uzun_url: str = Form(...), ozel_kod: str = Form(None)):
    # Kullanıcı http:// yazmayı unutursa otomatik ekle
    if not (uzun_url.startswith("http://") or uzun_url.startswith("https://")):
        uzun_url = "https://" + uzun_url

    db = Oturum()
    
    # URL daha önce kısaltılmış mı diye veritabanına bak
    mevcut = db.query(Link).filter(Link.uzun_url == uzun_url).first()
    if mevcut and not ozel_kod: # Eğer adam özel kod istediyse aynı url'yi tekrar ekleyebilir
        db.close()
        return RedirectResponse(url="/", status_code=303) 

    # Özel kod varsa onu kullan, yoksa rastgele üret
    if ozel_kod:
        kod_var_mi = db.query(Link).filter(Link.kisa_kod == ozel_kod).first()
        if kod_var_mi:
            db.close()
            return RedirectResponse(url="/?hata=kod_kullanimda", status_code=303)
        yeni_kod = ozel_kod
    else:
        yeni_kod = kisa_kod_uret()
    yeni_link = Link(uzun_url=uzun_url, kisa_kod=yeni_kod)
    
    db.add(yeni_link)
    db.commit()
    db.close()
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/sil/{link_id}")
def link_sil(link_id: int):
    db = Oturum()
    silinecek = db.query(Link).filter(Link.id == link_id).first()
    if silinecek:
        db.delete(silinecek)
        db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

# DİKKAT: Burası Yönlendirme (Redirect) Rotasıdır!
@app.get("/{kisa_kod}")
def yonlendir(kisa_kod: str):
    db = Oturum()
    link = db.query(Link).filter(Link.kisa_kod == kisa_kod).first()
    
    if link:
        # Biri bu linke tıkladığı için Analytics (Tıklanma) sayacını 1 artır!
        link.tiklanma_sayisi += 1
        db.commit()
        uzun_url = link.uzun_url
        db.close()
        
        # Kullanıcıyı hedefine fırlat (307 Temporary Redirect)
        return RedirectResponse(url=uzun_url, status_code=307)
        
    db.close()
    raise HTTPException(status_code=404, detail="Böyle bir kısa link bulunamadı!")
