from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import traceback
import uvicorn

app = FastAPI()

# ==========================================
# 1. TELEGRAM BOT AYARLARI
# ==========================================
# DİKKAT: BotFather'dan aldığın Token ve userinfobot'tan aldığın Chat ID'yi buraya gir.
# (Eğer girmezsen kod çalışır ama Telegram'a mesaj gitmez)
TELEGRAM_BOT_TOKEN = "TOKEN_BURAYA_GELECEK"
TELEGRAM_CHAT_ID = "CHAT_ID_BURAYA_GELECEK"


async def telegrama_hata_gonder(hata_mesaji: str):
    """
    Kendi botumuz üzerinden kendi cep telefonumuza mesaj fırlatan özel kurye fonksiyon.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🚨 <b>KRİTİK SUNUCU HATASI</b> 🚨\n\n{hata_mesaji}",
        "parse_mode": "HTML"
    }
    
    # httpx ile Telegram'ın REST API'sine POST isteği (Mesaj paketi) atıyoruz
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception:
            # Telegram'a mesaj atarken internet koparsa, ana sunucuyu çökertmemek için "pass" diyoruz.
            pass


# ==========================================
# 2. GİZLİ MİDDLEWARE (HATA YAKALAYICI KANCA)
# ==========================================
@app.middleware("http")
async def hata_yakalayici_middleware(request: Request, call_next):
    """
    Bu fonksiyon tüm uygulamanın tepesinde bir Kartal gibi uçar.
    Herhangi bir rotada hata (Exception) patlarsa, onu havada kapar.
    """
    try:
        # İsteğin normal bir şekilde yola devam edip rotalara gitmesine izin ver
        response = await call_next(request)
        return response
    
    except Exception as e:
        # Eğer içerideki herhangi bir rotada hata (Örn: 1/0) patlarsa, sistem ÇÖKMEZ, direkt buraya düşer!
        hata_kodu = str(e)
        
        # Hatayı anında kendi cep telefonumuza (Telegram'a) fırlatıyoruz
        await telegrama_hata_gonder(f"<b>Rota:</b> {request.url}\n\n<b>Hata Özeti:</b> <code>{hata_kodu}</code>")
        
        # Müşteriye ise (çirkin ve güvenlik açığı oluşturan kodlar göstermek yerine) temiz bir mesaj dönüyoruz.
        return JSONResponse(
            status_code=500,
            content={"hata": "Sunucuda beklenmedik bir sorun oluştu. Teknik ekibe (Yusuf'a) Telegram üzerinden anında haber verildi!"}
        )


# ==========================================
# 3. TEST ROTALARI
# ==========================================
@app.get("/")
async def anasayfa():
    return {"mesaj": "Sunucu kusursuz çalışıyor. Middleware'i test etmek için /hatali-rota adresine gir."}

@app.get("/hatali-rota")
async def hata_yap():
    # Burada kasten 1'i 0'a bölerek (ZeroDivisionError) bir hata patlatıyoruz.
    sonuc = 1 / 0
    
    # Bu yazı ASLA görünmeyecek çünkü üst satırda hata patlayacak ve Middleware bizi havada kapacak.
    return {"mesaj": sonuc}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 