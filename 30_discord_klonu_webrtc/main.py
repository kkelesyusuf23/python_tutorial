from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. SİNYAL SUNUCUSU (SIGNALING SERVER)
# ==========================================
# WebRTC (Ses/Görüntü), sunucu üzerinden AKMAZ! Bilgisayarlar doğrudan birbirine bağlanır (P2P).
# Ancak birbirlerini bulabilmeleri için bir "Tanışma" faslına ihtiyaçları vardır.
# Bu WebSocket sunucusunun TEK GÖREVİ, arabuluculuk (santral memurluğu) yapmaktır.
class SinyalSunucusu:
    def __init__(self):
        self.aktif_baglantilar: List[WebSocket] = []

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_baglantilar.append(websocket)

    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_baglantilar:
            self.aktif_baglantilar.remove(websocket)

    async def sinyali_digerlerine_yayinla(self, data: dict, gonderen: WebSocket):
        # A kişisinden gelen "Tanışma (Offer/Answer)" paketlerini,
        # kendisi hariç BÜTÜN odadakilere fırlat.
        for kisi in self.aktif_baglantilar:
            if kisi != gonderen:
                try:
                    await kisi.send_json(data)
                except:
                    pass


sinyal_sunucusu = SinyalSunucusu()

# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/sinyal")
async def websocket_sinyal(websocket: WebSocket):
    await sinyal_sunucusu.baglan(websocket)
    try:
        while True:
            # İstemciden WebRTC tanışma paketleri (Offer, Answer, ICE Candidate) gelir
            data = await websocket.receive_json()
            
            # Bu paketi olduğu gibi diğer kişiye yolla
            await sinyal_sunucusu.sinyali_digerlerine_yayinla(data, gonderen=websocket)
            
    except WebSocketDisconnect:
        sinyal_sunucusu.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 