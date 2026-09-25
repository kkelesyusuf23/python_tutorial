from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# ==========================================
# 1. MÜZAYEDE YÖNETİCİSİ (RACE CONDITION KORUMALI)
# ==========================================
class MuzayedeDurumu:
    def __init__(self):
        self.en_yuksek_teklif = 10000
        self.kazanan_isim = "Henüz Kimse"
        
        # SİHİRLİ KİLİT MEKANİZMASI (LOCK)
        # Bu kilit sayesinde aynı anda 1000 kişi teklif atsa bile, kilit kapıdan herkesi TEK TEK alır!
        self.kilit = asyncio.Lock()
        
        self.aktif_baglantilar: List[WebSocket] = []

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.aktif_baglantilar.append(websocket)
        # Odaya yeni girenlere anında masadaki fiyatı bildir
        await websocket.send_json({
            "fiyat": self.en_yuksek_teklif, 
            "isim": self.kazanan_isim, 
            "mesaj": "Odaya katıldınız. Teklif verebilirsiniz!"
        })

    def ayril(self, websocket: WebSocket):
        if websocket in self.aktif_baglantilar:
            self.aktif_baglantilar.remove(websocket)

    async def herkese_yayinla(self, data: dict):
        for oyuncu in self.aktif_baglantilar:
            await oyuncu.send_json(data)


muzayede = MuzayedeDurumu()

# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/teklif")
async def websocket_teklif(websocket: WebSocket):
    await muzayede.baglan(websocket)
    try:
        while True:
            # 1. Kullanıcıdan gelen teklifi yakala (Aynı milisaniyede 2 kişi yollamış olabilir!)
            data = await websocket.receive_json()
            gelen_teklif = data["teklif"]
            teklif_veren = data["isim"]
            
            # ========================================================
            # KRİTİK BÖLGE (CRITICAL SECTION) - YARIŞ DURUMU ENGELLENİYOR
            # async with kilit: kapısı açılır. İçeri sadece 1 kişi girebilir.
            # İçerideki kişi işlemi bitirmeden kapı 2. kişiye açılmaz!
            # ========================================================
            async with muzayede.kilit:
                
                # 2. İçeri giren kişinin teklifi, şu anki tablonun fiyatından büyük mü diye bak!
                # Neden buna bakıyoruz? Çünkü kapıda bekleyen 2. kişinin gönderdiği teklif,
                # 1. kişi yüzünden zaten eskimiş (düşük kalmış) olabilir!
                if gelen_teklif > muzayede.en_yuksek_teklif:
                    
                    # Veritabanını (Hafızayı) Güncelle
                    muzayede.en_yuksek_teklif = gelen_teklif
                    muzayede.kazanan_isim = teklif_veren
                    
                    # Odadaki herkese yeni Fiyatı (Lideri) anons et
                    await muzayede.herkese_yayinla({
                        "fiyat": muzayede.en_yuksek_teklif,
                        "isim": muzayede.kazanan_isim,
                        "mesaj": f"🔥 {teklif_veren} teklifi {gelen_teklif} TL'ye yükseltti!"
                    })
                
                else:
                    # Kapıda beklerken fiyat artmış! Teklifi geçersiz oldu!
                    await websocket.send_json({
                        "fiyat": muzayede.en_yuksek_teklif,
                        "isim": muzayede.kazanan_isim,
                        "mesaj": "❌ Teklifiniz geçersiz! Sizden önce davranan biri oldu."
                    })
            # --- KİLİT KAPANDI --- (Sıradaki kişi içeri alınır)
            
    except WebSocketDisconnect:
        muzayede.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
 