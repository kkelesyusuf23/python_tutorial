from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. BAĞLANTI YÖNETİCİSİ (COLLABORATION ENGINE)
# ==========================================
class DokumanYoneticisi:
    def __init__(self):
        self.aktif_baglantilar: List[WebSocket] = []

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_baglantilar.append(websocket)

    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_baglantilar:
            self.aktif_baglantilar.remove(websocket)

    async def digerlerine_yayinla(self, data: dict, gonderen: WebSocket):
        # NOT: Önceki projelerde mesajı herkese (gönderen dahil) yolluyorduk.
        # Ancak burada OT (Operational Transformation) kuralları gereği, 
        # değişimi yapan kişiye KENDİ DEĞİŞİKLİĞİNİ geri yollamıyoruz! 
        # Sadece diğer insanlara yolluyoruz ki kendi ekranı "çift yazma" yapmasın.
        for oyuncu in self.aktif_baglantilar:
            if oyuncu != gonderen:
                await oyuncu.send_json(data)


yonetici = DokumanYoneticisi()

# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/docs")
async def websocket_docs(websocket: WebSocket):
    await yonetici.baglan(websocket)
    try:
        while True:
            # Kullanıcı klavyeden bir harf sildiğinde veya eklediğinde "Delta" paketi gelir
            data = await websocket.receive_json()
            
            # Gelen bu paketi (Örn: "3. sıradaki harfi sil, yerine 'A' yaz") 
            # DİĞER TÜM KULLANICILARA anında fırlat.
            await yonetici.digerlerine_yayinla(data, gonderen=websocket)
            
    except WebSocketDisconnect:
        yonetici.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 