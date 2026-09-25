from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

app = FastAPI(title="API Gateway (Giriş Kapısı)")

# Mikroservislerin gizli adresleri (Müşteri bunları bilmez)
SIPARIS_SERVIS_URL = "http://127.0.0.1:8001"
KULLANICI_SERVIS_URL = "http://127.0.0.1:8002"

@app.get("/")
async def anasayfa():
    return {"mesaj": "API Gateway'e Hoşgeldin. /api/siparisler veya /api/kullanicilar rotalarını dene."}

# ==========================================
# 1. SİPARİŞ KÖPRÜSÜ (REVERSE PROXY)
# ==========================================
@app.get("/api/siparisler")
async def siparis_koprusu():
    async with httpx.AsyncClient() as client:
        try:
            # Müşteri bizden istedi, biz arka planda 8001'e gidip alıp geliyoruz (Kuryelik)
            cevap = await client.get(f"{SIPARIS_SERVIS_URL}/siparisler")
            return cevap.json()
        except httpx.RequestError:
            # SİPARİŞ SERVİSİ ÇÖKERSE GATEWAY ÇÖKMEZ! Sadece zarif bir hata döner.
            raise HTTPException(status_code=503, detail="Sipariş Mikroservisi şu an çöktü veya kapalı. Lütfen daha sonra deneyin.")

# ==========================================
# 2. KULLANICI KÖPRÜSÜ (REVERSE PROXY)
# ==========================================
@app.get("/api/kullanicilar")
async def kullanici_koprusu():
    async with httpx.AsyncClient() as client:
        try:
            cevap = await client.get(f"{KULLANICI_SERVIS_URL}/kullanicilar")
            return cevap.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Kullanıcı Mikroservisi ulaşılamıyor.")


if __name__ == "__main__":
    # Müşterinin (Uygulamanın) muhatap olacağı TEK kapı burasıdır (Port 8000)
    uvicorn.run("api_gateway:app", host="127.0.0.1", port=8000, reload=True)
 