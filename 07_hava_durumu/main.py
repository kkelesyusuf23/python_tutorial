from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import time
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Önbellekleme sözlüğü ve süresi (Saniye)
CACHE_BELLEK = {}
CACHE_SURESI = 600  # 10 dakika

@app.get("/", response_class=HTMLResponse)
async def ana_sayfa(request: Request):
    # İlk açılışta boş form
    return templates.TemplateResponse("index.html", {"request": request, "veri": None, "hata": None})

@app.get("/sorgula", response_class=HTMLResponse)
async def hava_durumu_sorgula(request: Request, sehir: str = ""):
    sehir = sehir.strip().title()
    if not sehir:
        return templates.TemplateResponse("index.html", {"request": request, "veri": None, "hata": "Lütfen geçerli bir şehir girin."})
         
    guncel_zaman = time.time()
    
    # 1. ÖN BELLEK (CACHE) KONTROLÜ
    if sehir in CACHE_BELLEK:
        kayit_zamani = CACHE_BELLEK[sehir]["timestamp"]
        if guncel_zaman - kayit_zamani < CACHE_SURESI:
            veri = CACHE_BELLEK[sehir]["veri"]
            # Cached=True parametresiyle gönderiyoruz
            return templates.TemplateResponse("index.html", {"request": request, "veri": veri, "hata": None, "cached": True})

    # 2. İNTERNETTEN VERİ ÇEKME (HTTPX)
    try:
        # httpx.AsyncClient kullanarak asenkron istek atıyoruz (Tarayıcıyı dondurmaz)
        async with httpx.AsyncClient() as client:
            # Adım 1: Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={sehir}&count=1&language=en&format=json"
            cevap = await client.get(geo_url)
            geo_veri = cevap.json()
            
            if not geo_veri.get("results"):
                return templates.TemplateResponse("index.html", {"request": request, "veri": None, "hata": f"'{sehir}' bulunamadı!"})
                
            enlem = geo_veri["results"][0]["latitude"]
            boylam = geo_veri["results"][0]["longitude"]
            ulke = geo_veri["results"][0].get("country", "")
            
            # Adım 2: Hava Durumu
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true"
            cevap2 = await client.get(weather_url)
            weather_veri = cevap2.json()
            
            anlik = weather_veri["current_weather"]
            
            # Paketi hazırla
            paket = {
                "sehir": sehir,
                "ulke": ulke,
                "sicaklik": anlik["temperature"],
                "ruzgar": anlik["windspeed"]
            }
            
            # Önbelleğe (Cache) Kaydet
            CACHE_BELLEK[sehir] = {
                "veri": paket,
                "timestamp": guncel_zaman
            }
            
            return templates.TemplateResponse("index.html", {"request": request, "veri": paket, "hata": None, "cached": False})
            
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "veri": None, "hata": "API Bağlantı hatası oluştu."})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
