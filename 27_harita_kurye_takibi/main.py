from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. BAĞLANTI YÖNETİCİSİ (BROADCAST ENGINE)
# ==========================================
class KuryeTakipSistemi:
    def __init__(self):
        self.aktif_baglantilar: List[WebSocket] = []
        
        # Başlangıç Koordinatları (İstanbul - Taksim Meydanı civarı)
        self.kurye_enlem = 41.0369
        self.kurye_boylam = 28.9850

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_baglantilar.append(websocket)
        # Yeni müşteri bağlandığında kuryenin güncel konumunu hemen yolla ki harita ortalansın
        await websocket.send_json({"enlem": self.kurye_enlem, "boylam": self.kurye_boylam})

    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_baglantilar:
            self.aktif_baglantilar.remove(websocket)

    async def herkese_yayinla(self, data: dict):
        for musteri in self.aktif_baglantilar:
            try:
                await musteri.send_json(data)
            except:
                pass

kurye_sistemi = KuryeTakipSistemi()


# ==========================================
# 2. ARKA PLAN KURYE MOTORU (SİMÜLASYON)
# ==========================================
async def kurye_hareket_motoru():
    while True:
        # Kuryemiz her 1 saniyede harita üzerinde hafifçe ilerliyor (Güney-Doğu yönüne doğru)
        kurye_sistemi.kurye_enlem -= 0.0001
        kurye_sistemi.kurye_boylam += 0.0001
        
        # Yeni lokasyonu tüm müşterilere (WebSockets) anında fırlat
        await kurye_sistemi.herkese_yayinla({
            "enlem": kurye_sistemi.kurye_enlem,
            "boylam": kurye_sistemi.kurye_boylam
        })
        
        # Sistemin yorulmaması için 1 saniye uyu ve tekrar hareket et
        await asyncio.sleep(1)

# Sunucu başlar başlamaz kuryeyi yola çıkartan özel FastAPI olayı (Event)
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kurye_hareket_motoru())


# ==========================================
# 3. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/takip")
async def websocket_takip(websocket: WebSocket):
    await kurye_sistemi.baglan(websocket)
    try:
        while True:
            # Müşteriden bir veri beklemiyoruz. Müşteri sadece izleyici (Receiver).
            # Tünelin açık kalması için bu sonsuz döngü şarttır.
            await websocket.receive_text()
    except WebSocketDisconnect:
        kurye_sistemi.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 