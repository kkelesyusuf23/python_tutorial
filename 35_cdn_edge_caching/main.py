import time
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI()

# ==========================================
# 1. IN-MEMORY CACHE (RAM ÖN BELLEK)
# ==========================================
# Geleneksel veritabanı veya Hard Disk yerine verileri Işık Hızında işleyen RAM'i kullanacağız.
RAM_ONBELLEK = {}
ASSET_YOLU = "assets/logo.png"


@app.get("/")
def anasayfa():
    # Tarayıcı bu HTML'i okuduğu an, otomatik olarak <img src="/resim" /> diyerek sunucumuza 2. bir istek atacak.
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Kendi Süper Hızlı CDN'imiz</title>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;800&display=swap" rel="stylesheet">
            <style>body { font-family: 'Outfit', sans-serif; background: #0f172a; color: white; text-align: center; margin-top: 50px; }</style>
        </head>
        <body>
            <h1>Mükemmel Hızlı CDN Mimarisi ⚡</h1>
            <p style="color: #94a3b8">Aşağıdaki resim sunucunun RAM'inden (ya da senin tarayıcı önbelleğinden) geliyor:</p>
            
            <img src="/resim" alt="CDN Logo" style="width:300px; height:300px; border-radius:20px; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.5); object-fit: cover; background: #1e293b;"/>
            
            <br><br>
            <h3 style="color: #10b981">Test Etmek İçin:</h3>
            <p>1. Terminal (Konsol) pencerene bak, ilk yükleme süresini gör.</p>
            <p>2. Sayfayı yenile ve RAM sayesinde (Cache Hit) sürenin nasıl kısaldığını (Milisaniyelere düştüğünü) izle!</p>
        </body>
    </html>
    """)


@app.get("/resim")
def resim_getir(response: Response):
    baslangic_zamani = time.perf_counter()
    
    # EĞER RESİM DAHA ÖNCE RAM'E ALINDI YSA (CACHE HIT)
    if ASSET_YOLU in RAM_ONBELLEK:
        dosya_icerigi = RAM_ONBELLEK[ASSET_YOLU]
        islem_tipi = "🚀 HIZLI: RAM'den okundu (Cache Hit)"
        
    # EĞER RESİM İLK DEFA İSTENİYORSA VEYA RAM'DE YOKSA (CACHE MISS)
    else:
        # Hard diskteki dosyayı aç (SSD/HDD okumaları çok maliyetlidir)
        with open(ASSET_YOLU, "rb") as dosya:
            dosya_icerigi = dosya.read()
            
            # Hard diskten okuduğumuz bu ağır dosyayı hemen RAM'e (Sözlüğe) kopyalıyoruz
            RAM_ONBELLEK[ASSET_YOLU] = dosya_icerigi
            islem_tipi = "🐌 YAVAŞ: Hard Diskten okundu (Cache Miss)"
            
    bitis_zamani = time.perf_counter()
    gecen_sure = (bitis_zamani - baslangic_zamani) * 1000 # Milisaniye cinsinden
    
    # Loglama yapıyoruz ki Hız farkını terminalde canlı görelim
    print(f"[{islem_tipi}] - Geçen Süre: {gecen_sure:.4f} milisaniye")
    
    
    # ==========================================
    # 2. EDGE CACHING (HTTP CACHE-CONTROL)
    # ==========================================
    # Müşterinin tarayıcısına (Örn: Chrome, Safari) şu sert emri veriyoruz: 
    # "Bu resmi aldın, 1 YIL (31536000 saniye) boyunca benden bir daha İSTEME! Kendi içine (Browser Cache) kaydet."
    # Böylece aynı müşteri siteye yarın girdiğinde, bizim sunucumuza istek HİÇ GELMEZ! Tarayıcı kendi içinden resmi yükler.
    response.headers["Cache-Control"] = "public, max-age=31536000"
    
    return Response(content=dosya_icerigi, media_type="image/png")


if __name__ == "__main__":
    # Test ortamı için sahte bir 1 MB'lık resim (Binary veri) yaratıyoruz. (Eğer yoksa)
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists(ASSET_YOLU):
        with open(ASSET_YOLU, "wb") as f:
            f.write(os.urandom(1024 * 1024)) # 1 Megabayt rastgele veri
            
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 