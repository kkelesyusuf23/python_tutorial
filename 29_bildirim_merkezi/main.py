import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import random
import json
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Sahte isimler ve eylemler (Instagram tarzı)
KULLANICILAR = ["ahmet123", "zeynep_x", "mehmet.yilmaz", "ayse_nur", "yuke", "zeak"]
EYLEMLER = [
    "fotoğrafını beğendi. ❤️", 
    "seni takip etmeye başladı. 👤", 
    "hikayene yanıt verdi. 💬", 
    "gönderine yorum yaptı. 📝"
]

# ==========================================
# 1. BİLDİRİM ÜRETİCİ (ASENKRON JENERATÖR - YIELD)
# ==========================================
async def bildirim_olusturucu():
    """
    Bu fonksiyon standart bir 'return' yapmak yerine, 'yield' kullanarak
    asla kapanmayan (Sonsuz) bir veri akışı (Stream) yaratır.
    """
    while True:
        # 2 ile 5 saniye arası rastgele bekle
        bekleme_suresi = random.randint(2, 5)
        await asyncio.sleep(bekleme_suresi)
        
        # Sahte bir bildirim oluştur
        kisi = random.choice(KULLANICILAR)
        eylem = random.choice(EYLEMLER)
        saat = datetime.now().strftime("%H:%M:%S")
        
        bildirim_verisi = {
            "mesaj": f"<b>{kisi}</b> {eylem}",
            "zaman": saat
        }
        
        # DİKKAT: Server-Sent Events protokolü katı bir kurala sahiptir.
        # Gönderilen metin her zaman "data: " ile başlamalı ve "\n\n" ile bitmelidir.
        yield f"data: {json.dumps(bildirim_verisi)}\n\n"


# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/bildirimler")
async def sse_bildirim_rotasi():
    """
    Standart HTML veya JSON dönmek yerine, yukarıdaki bildirim üreticisini 
    text/event-stream formatında (SSE formatı) tarayıcıya bağlıyoruz.
    Bu tünel, tarayıcı sayfayı kapatana kadar ASLA kapanmaz.
    """
    return StreamingResponse(bildirim_olusturucu(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 