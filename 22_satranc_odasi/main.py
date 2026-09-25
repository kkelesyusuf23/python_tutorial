from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ========================================================
# 1. BAĞLANTI YÖNETİCİSİ (CONNECTION MANAGER)
# ========================================================
# Oyuna giren kişileri bir "Odada" toplamak için bu sınıfı kullanıyoruz.
class OyunOdasi:
    def __init__(self):
        # Odaya bağlanan oyuncuların WebSocket tünellerini bu listede tutacağız.
        self.aktif_oyuncular: List[WebSocket] = []
        
        # Satranç tahtasının o anki dizilimini (FEN formatı) hafızada tutuyoruz.
        # "start", satrancın varsayılan başlangıç dizilimidir.
        self.oyun_durumu = "start"

    # Yeni biri sayfaya girdiğinde onu odaya alırız
    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_oyuncular.append(websocket)
        
        # Oyuncu masaya yeni oturduğu için, ona masanın güncel halini (FEN) gönderiyoruz.
        # Böylece oyuna sonradan girenler bile tahtanın son halini görür.
        await websocket.send_json({"tur": "guncelleme", "fen": self.oyun_durumu})

    # Biri sekmeyi kapatırsa odadan çıkarırız
    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_oyuncular:
            self.aktif_oyuncular.remove(websocket)

    # Bir oyuncu hamle yaptığında, bu hamleyi (mesajı) ODADAKİ HERKESE yollarız (YAYIN/BROADCAST)
    async def herkese_yayinla(self, mesaj: dict, gonderen: WebSocket):
        for oyuncu in self.aktif_oyuncular:
            # Gönderen kişiye kendi hamlesini tekrar göndermiyoruz (Eko olmasın diye)
            if oyuncu != gonderen:
                await oyuncu.send_json(mesaj)

# Sınıfımızdan tek bir oyun odası nesnesi yaratıyoruz
satranc_odasi = OyunOdasi()


# ========================================================
# 2. ROTALAR (WEB SAYFASI VE WEBSOCKET TÜNELİ)
# ========================================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/satranc")
async def satranc_socket(websocket: WebSocket):
    # 1. Adım: Kullanıcıyı odaya al
    await satranc_odasi.baglan(websocket)
    print(f"Odadaki oyuncu sayısı: {len(satranc_odasi.aktif_oyuncular)}")
    
    try:
        # 2. Adım: Kullanıcıdan (Tarayıcıdan) hamle gelmesini sonsuza kadar bekle
        while True:
            gelen_veri = await websocket.receive_json()
            
            # Eğer kullanıcı bir taş oynattıysa (Örn: e2 piyonu e4'e gitti)
            if gelen_veri["tur"] == "hamle":
                # Yeni taş dizilimini (FEN) odanın hafızasına kaydet
                satranc_odasi.oyun_durumu = gelen_veri["fen"]
                
                # Bu hamleyi diğer oyuncuya (Rakibe) fırlat!
                await satranc_odasi.herkese_yayinla(gelen_veri, gonderen=websocket)
                
    except WebSocketDisconnect:
        # 3. Adım: Oyuncu kaçarsa odadan sil
        satranc_odasi.ayril(websocket)
        print("Bir oyuncu masadan ayrıldı.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 