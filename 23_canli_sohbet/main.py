from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from tinydb import TinyDB
import uvicorn
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# NoSQL VERİTABANI BAŞLATILIYOR (TinyDB)
# Tüm mesajlar esnek dökümanlar halinde (JSON) bu dosyada saklanacak
# ==========================================
db = TinyDB("mesajlar.json")


# ==========================================
# 1. BAĞLANTI YÖNETİCİSİ (CONNECTION MANAGER)
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.aktif_baglantilar: List[WebSocket] = []

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_baglantilar.append(websocket)

    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_baglantilar:
            self.aktif_baglantilar.remove(websocket)

    async def herkese_yayinla(self, mesaj_dict: dict):
        # Bu projede gönderene de geri yolluyoruz (Çift tik mantığı, gönderildiğini anlasın)
        for oyuncu in self.aktif_baglantilar:
            await oyuncu.send_json(mesaj_dict)

oda_yoneticisi = ConnectionManager()


# ==========================================
# 2. ROTALAR (HTTP ve WEBSOCKET)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    # Veritabanındaki tüm eski (Şifreli) mesajları çek
    eski_kayitlar = db.all()
    # HTML şablonuna bu şifreli kayıtları gönder (Javascript sayfada şifrelerini çözecek)
    return templates.TemplateResponse("index.html", {"request": request, "eski_mesajlar": eski_kayitlar})

@app.websocket("/ws/sohbet")
async def websocket_sohbet(websocket: WebSocket):
    await oda_yoneticisi.baglan(websocket)
    try:
        while True:
            # 1. Tarayıcıdan gelen JSON mesajını al
            data = await websocket.receive_json()
            
            # 2. DİKKAT (E2EE): data["metin"] şuan şifreli (Örn: U2FsdGVkX1...)
            # Sunucu olarak gizli anahtarı bilmediğimiz için okuyamıyoruz. 
            # Sadece körü körüne (MongoDB mantığıyla) veritabanına yazıyoruz.
            db.insert(data)
            
            # 3. Bu şifreli mesajı (hiç dokunmadan) sohbetteki herkese fırlat
            await oda_yoneticisi.herkese_yayinla(data)
            
    except WebSocketDisconnect:
        oda_yoneticisi.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)