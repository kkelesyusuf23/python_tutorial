from fastapi import FastAPI
import httpx
from veritabani import Oturum, Replik
from pydantic import BaseModel


app = FastAPI()

class YeniReplikIstegi(BaseModel):
    film_adi:str
    karakter:str
    soz:str


@app.get("/rastgele-replik-cek")
async def rastgele_replik_cek():
    async with httpx.AsyncClient() as istemci:
        cevap = await istemci.get("https://dummyjson.com/quotes/random")
        veri = cevap.json()

        gelen_yazar = veri.get("author")
        gelen_soz = veri.get("quote")

    
    db = Oturum()

    yeni_replik = Replik(film_adi="Bilinmeyen Film", karakter=gelen_yazar, soz=gelen_soz)
    
    db.add(yeni_replik) # Veritabanına ekle
    db.commit()         # Kaydet
    db.refresh(yeni_replik) # ID numarasını alması için tazele
    db.close()          # Kapıyı kapat
    
    # 3. Sonucu kullanıcıya gösteriyoruz
    return {
        "mesaj": "Veri başarıyla çekildi ve veritabanına kaydedildi!",
        "kaydedilen_veri": {
            "id": yeni_replik.id,
            "karakter": yeni_replik.karakter,
            "soz": yeni_replik.soz
        }
    }


@app.get("/tum-replikler")
def tum_replikleri_getir():
    db = Oturum()
    # SQL yerine direkt Python koduyla tüm satırları getiriyoruz!
    tum_veriler = db.query(Replik).all()
    db.close()
    
    return tum_veriler


# Veritabanına dışarıdan manuel veri ekleyen Endpoint
@app.post("/manuel-replik-ekle")
def manuel_replik_ekle(istek: YeniReplikIstegi):
    db = Oturum()
    
    # Kullanıcıdan gelen (istek) verilerle yeni bir nesne oluştur
    yeni_replik = Replik(
        film_adi=istek.film_adi, 
        karakter=istek.karakter, 
        soz=istek.soz
    )
    
    db.add(yeni_replik)
    db.commit()
    db.refresh(yeni_replik)
    db.close()
    
    return {"mesaj": "Başarıyla eklendi!", "eklenen_veri": yeni_replik.id}
