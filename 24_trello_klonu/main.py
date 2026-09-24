from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from tinydb import TinyDB, Query
import uvicorn
import uuid
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# NoSQL Veritabanı: Kanban panosundaki görevler burada saklanır
db = TinyDB("kanban.json")

# ==========================================
# 1. BAĞLANTI YÖNETİCİSİ (BROADCAST ENGINE)
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
        for oyuncu in self.aktif_baglantilar:
            await oyuncu.send_json(mesaj_dict)

yonetici = ConnectionManager()


# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    # Sayfa ilk yüklendiğinde veritabanındaki tüm görevleri (kartları) çekip ekrana basıyoruz
    gorevler = db.all()
    return templates.TemplateResponse("index.html", {"request": request, "gorevler": gorevler})

@app.websocket("/ws/trello")
async def websocket_trello(websocket: WebSocket):
    await yonetici.baglan(websocket)
    try:
        while True:
            # İstemciden gelen isteği (JSON) al
            data = await websocket.receive_json()
            Gorev = Query() # TinyDB sorgu nesnesi
            
            # DURUM 1: Kullanıcı yeni bir görev kartı eklemek istiyorsa
            if data["tur"] == "yeni_gorev":
                yeni_id = str(uuid.uuid4()) # Benzersiz bir ID üret
                yeni_gorev = {"id": yeni_id, "baslik": data["baslik"], "sutun": "todo"}
                
                # Veritabanına kaydet
                db.insert(yeni_gorev)
                
                # Odadaki herkese "Yeni kart eklendi, ekranınızı güncelleyin!" diye bağır
                await yonetici.herkese_yayinla({"tur": "yeni_gorev", "gorev": yeni_gorev})
                
            # DURUM 2: Kullanıcı bir kartı farenin ucuyla alıp başka bir sütuna bıraktıysa (Update)
            elif data["tur"] == "tasi":
                # Veritabanındaki o görevi bul ve sadece "sutun" değerini (Örn: todo -> done) değiştir
                db.update({"sutun": data["hedef_sutun"]}, Gorev.id == data["id"])
                
                # Odadaki herkese (ve taşıyan kişiye) kartın yeni yerini bildir
                await yonetici.herkese_yayinla({"tur": "tasi", "id": data["id"], "hedef_sutun": data["hedef_sutun"]})
                
    except WebSocketDisconnect:
        yonetici.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
