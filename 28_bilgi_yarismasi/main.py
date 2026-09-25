from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import time

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Veritabanı yerine hafızadaki basit soru havuzu
SORULAR = [
    {"soru": "Dünyanın en büyük okyanusu hangisidir?", "secenekler": ["Atlas", "Büyük (Pasifik)", "Hint", "Arktik"], "cevap": "Büyük (Pasifik)"},
    {"soru": "Python programlama dilinin yaratıcısı kimdir?", "secenekler": ["Bill Gates", "Guido van Rossum", "Linus Torvalds", "Elon Musk"], "cevap": "Guido van Rossum"},
    {"soru": "Aşağıdakilerden hangisi bir NoSQL veritabanıdır?", "secenekler": ["MySQL", "PostgreSQL", "MongoDB", "Oracle"], "cevap": "MongoDB"}
]

# ==========================================
# 1. OYUN MOTORU VE DURUM MAKİNESİ (STATE MACHINE)
# ==========================================
class KahootMotoru:
    def __init__(self):
        # Odaya giren oyuncuları ve puanlarını burada tutacağız
        self.oyuncular = {} # Örn: {websocket: {"isim": "Ahmet", "puan": 0}}
        self.aktif_soru_index = 0
        self.soru_baslangic_zamani = 0
        self.dogru_cevap = ""
        self.oyun_durumu = "bekleme" # Oyunun o anki durumu: 'bekleme', 'soru', 'skor'

    async def baglan(self, websocket: WebSocket):
        await websocket.accept()
        self.oyuncular[websocket] = {"isim": "Misafir", "puan": 0}

    def ayril(self, websocket: WebSocket):
        if websocket in self.oyuncular:
            del self.oyuncular[websocket]

    async def herkese_yayinla(self, data: dict):
        for oyuncu in list(self.oyuncular.keys()):
            try:
                await oyuncu.send_json(data)
            except:
                pass

    # Kilit Nokta: Sürekli Arkada Çalışan Oyun Döngüsü
    async def oyun_dongusu(self):
        while True:
            # Odada kimse yoksa oyunu başlatma
            if len(self.oyuncular) == 0:
                await asyncio.sleep(2)
                continue
                
            # Bütün sorular bittiyse oyunu sıfırla
            if self.aktif_soru_index >= len(SORULAR):
                await self.herkese_yayinla({"tur": "bitis", "mesaj": "🏆 Yarışma Bitti!"})
                await asyncio.sleep(10) # 10 sn şampiyonları ekranda tut
                self.aktif_soru_index = 0
                for oyuncu in self.oyuncular.values():
                    oyuncu["puan"] = 0 # Puanları sıfırla yeni maça geç
                continue

            # --- AŞAMA 1: SORUYU YAYINLA ---
            self.oyun_durumu = "soru"
            soru = SORULAR[self.aktif_soru_index]
            self.dogru_cevap = soru["cevap"]
            self.soru_baslangic_zamani = time.time()
            
            await self.herkese_yayinla({
                "tur": "soru",
                "soru": soru["soru"],
                "secenekler": soru["secenekler"],
                "sure": 10 # 10 saniye süre ver
            })
            
            # Sunucu tam 10 saniye uykuda bekler (Bu sırada kullanıcılar cevap atar)
            await asyncio.sleep(10)
            
            # --- AŞAMA 2: SKORLARI YAYINLA ---
            self.oyun_durumu = "skor"
            # Oyuncuları puanlarına göre yüksekten düşüğe sıralar
            liderlik_tablosu = sorted([{"isim": p["isim"], "puan": p["puan"]} for p in self.oyuncular.values()], key=lambda x: x["puan"], reverse=True)
            
            await self.herkese_yayinla({
                "tur": "skor",
                "dogru_cevap": self.dogru_cevap,
                "liderlik": liderlik_tablosu
            })
            
            self.aktif_soru_index += 1
            
            # Sonraki soruya geçmeden 5 saniye mola (Dinlenme payı)
            await asyncio.sleep(5)

oyun_motoru = KahootMotoru()

# FastAPI başlar başlamaz Oyun Motorunu arkada sonsuz döngüye sok
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(oyun_motoru.oyun_dongusu())

# ==========================================
# 2. ROTALAR
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/yarisma")
async def websocket_yarisma(websocket: WebSocket):
    await oyun_motoru.baglan(websocket)
    try:
        while True:
            # Kullanıcılardan gelen veri (Giriş veya Cevap)
            data = await websocket.receive_json()
            
            # Oyuncu sisteme adını girmişse
            if data["tur"] == "giris":
                oyun_motoru.oyuncular[websocket]["isim"] = data["isim"]
            
            # Oyuncu soruyu cevaplamışsa
            elif data["tur"] == "cevap":
                # Sadece soru aşamasındayken cevap kabul et (Geç kalanlar sayılmaz)
                if oyun_motoru.oyun_durumu == "soru":
                    gecen_sure = time.time() - oyun_motoru.soru_baslangic_zamani
                    
                    if data["cevap"] == oyun_motoru.dogru_cevap:
                        # Ne kadar erken bilirse o kadar yüksek puan kazanır (1 sn = 90 Puan, 9 sn = 10 Puan)
                        kazanilan_puan = int(max(0, 10 - gecen_sure) * 10)
                        oyun_motoru.oyuncular[websocket]["puan"] += kazanilan_puan
                        
    except WebSocketDisconnect:
        oyun_motoru.ayril(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
