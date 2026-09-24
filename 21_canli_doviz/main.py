import asyncio
import random
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Başlangıç Döviz/Emtia Fiyatları (Sunucu hafızasında tutulur)
doviz_verileri = {
    "USD/TRY": 34.12,
    "EUR/TRY": 37.45,
    "ALTIN": 2500.50,
    "GBP/TRY": 44.10,
    "CHF/TRY": 39.80,
    "GÜMÜŞ": 32.15
}

@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    # Sayfa ilk açıldığında fiyatları statik olarak gönderiyoruz (Tünel açılana kadar boş kalmasın diye)
    return templates.TemplateResponse("index.html", {"request": request, "dovizler": doviz_verileri})

# === SİHİR BURADA BAŞLIYOR: WEBSOCKET ROTASI ===
@app.websocket("/ws/doviz")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Kullanıcıdan gelen "Tünel açma" (Connection) talebini kabul et
    await websocket.accept()
    print("Yeni bir WebSocket istemcisi bağlandı!")
    
    try:
        # 2. Bağlantı açık kaldığı sürece sonsuz bir döngüde dön
        while True:
            # Saniyede 1 kez veri pompala (Gerçek borsalarda bu nanosaniyedir)
            await asyncio.sleep(1)
            degisiklik_var = False
            
            # Gerçek veri olmadığı için fiyatları yapay olarak dalgalandırıyoruz
            for sembol in doviz_verileri.keys():
                # Her coinin/dövizin her saniye değişme ihtimalini %50 yapıyoruz
                if random.random() > 0.5:
                    degisim = random.uniform(-0.15, 0.15) # -0.15 ile +0.15 arası kuruş değişimi
                    doviz_verileri[sembol] = round(doviz_verileri[sembol] + degisim, 2)
                    degisiklik_var = True
            
            # Eğer en az 1 dövizin fiyatı değiştiyse, YENİ JSON DATASINI TÜNELDEN KULLANICIYA FIRLAT (PUSH)
            if degisiklik_var:
                await websocket.send_json(doviz_verileri)
                
    except WebSocketDisconnect:
        # Eğer kullanıcı sekmeyi kapatırsa bağlantı kopar
        print("İstemci WebSocket bağlantısını kesti.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
