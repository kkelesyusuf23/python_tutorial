import aiohttp
import asyncio
import json
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# === 1. KALICI VERİTABANI İŞLEMLERİ (JSON) ===
JSON_DOSYASI = "portfoy.json"

if os.path.exists(JSON_DOSYASI):
    with open(JSON_DOSYASI, "r", encoding="utf-8") as f:
        COIN_LISTESI = json.load(f)
else:
    COIN_LISTESI = []

def json_kaydet():
    with open(JSON_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(COIN_LISTESI, f, indent=4, ensure_ascii=False)


# === 2. HARİCİ API (COINGECKO) İLE GERÇEK İSİM VE LOGO BULMA ===
async def logo_ve_isim_bul(kisaltma: str):
    url = f"https://api.coingecko.com/api/v3/search?query={kisaltma}"
    # Bu istek asenkron çalışır ve sunucuyu/kullanıcıyı meşgul etmez
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    veri = await response.json()
                    # Eğer CoinGecko aramasından sonuç döndüyse
                    if veri.get("coins") and len(veri["coins"]) > 0:
                        en_iyi_sonuc = veri["coins"][0]
                        gercek_isim = en_iyi_sonuc.get("name")
                        gercek_logo = en_iyi_sonuc.get("thumb")
                        
                        # Hafızadaki listemizi güncelliyoruz
                        for coin in COIN_LISTESI:
                            if coin["kisaltma"] == kisaltma:
                                coin["isim"] = gercek_isim
                                coin["logo"] = gercek_logo
                                # JSON dosyasına kalıcı olarak yazıyoruz
                                json_kaydet()
                                break
        except Exception as e:
            print("CoinGecko Arama Hatası:", e)


# === 3. STANDART ASENKRON BİNANCE İSTEKLERİ ===
async def fiyat_cek(session, coin_bilgisi):
    try:
        async with session.get(coin_bilgisi["url"]) as response:
            veri = await response.json()
            ham_fiyat = float(veri["price"])
            fiyat = round(ham_fiyat, 4) if ham_fiyat < 10 else round(ham_fiyat, 2)
            
            return {
                "isim": coin_bilgisi["isim"],
                "kisaltma": coin_bilgisi["kisaltma"],
                "logo": coin_bilgisi["logo"],
                "fiyat": f"$ {fiyat:,.4f}" if ham_fiyat < 10 else f"$ {fiyat:,.2f}",
                "durum": "basarili"
            }
    except Exception:
        return {
            "isim": coin_bilgisi["isim"],
            "kisaltma": coin_bilgisi["kisaltma"],
            "logo": coin_bilgisi["logo"],
            "fiyat": "Hata",
            "durum": "hata"
        }

@app.get("/", response_class=HTMLResponse)
async def portfoy_sayfasi(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "coinler": COIN_LISTESI})

@app.get("/api/fiyatlar")
async def api_fiyatlar():
    async with aiohttp.ClientSession() as session:
        gorevler = [fiyat_cek(session, coin) for coin in COIN_LISTESI]
        sonuclar = await asyncio.gather(*gorevler)
    return {"coinler": sonuclar}


class YeniCoin(BaseModel):
    kisaltma: str

@app.post("/api/coin-ekle")
async def coin_ekle(coin_istek: YeniCoin):
    kisaltma = coin_istek.kisaltma.upper().strip()
    
    for coin in COIN_LISTESI:
        if coin["kisaltma"] == kisaltma:
            return {"mesaj": "Bu coin portföyde zaten var!", "durum": "hata"}
            
    binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={kisaltma}USDT"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(binance_url) as response:
            if response.status == 200:
                # Kullanıcıyı bekletmemek için HIZLICA geçici logoyla (⏳) ekliyoruz
                COIN_LISTESI.append({
                    "isim": kisaltma,
                    "kisaltma": kisaltma,
                    "logo": "⏳",
                    "url": binance_url
                })
                json_kaydet() # Sisteme yazalım ki çökse bile gitmesin
                
                # Büyü burada: Biz 0.1 saniyede kullanıcıya "Başarılı" dönüyoruz,
                # ama ARKADAN kendi kendine çalışan bağımsız bir görev başlatıyoruz (Fire and Forget)
                asyncio.create_task(logo_ve_isim_bul(kisaltma))
                
                return {"mesaj": f"{kisaltma} eklendi! Gerçek logoları indiriliyor...", "durum": "basarili"}
            else:
                return {"mesaj": f"Binance'de '{kisaltma}' bulunamadı.", "durum": "hata"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 