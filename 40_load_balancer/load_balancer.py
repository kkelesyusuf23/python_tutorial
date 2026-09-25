from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

app = FastAPI(title="Kendi Nginx'imiz (Load Balancer)")

# Arka planda çalışan 3 gizli sunucumuzun (Kopyaların) listesi
SUNUCULAR = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003"
]

# Round-Robin algoritması için sayacımız (Kimlik numarası)
SIRADAKI_SUNUCU_INDEX = 0

@app.get("/")
async def trafigi_dengele():
    """ 
    Dış dünyadan (Müşterilerden) 8000 portuna gelen istekleri karşılar
    ve Round-Robin ile sıradaki arka sunucuya iletir.
    """
    global SIRADAKI_SUNUCU_INDEX
    
    # 1. Sıradaki hedef sunucuyu seç (Örn: 8001)
    hedef_sunucu = SUNUCULAR[SIRADAKI_SUNUCU_INDEX]
    
    # 2. Sayacı bir artır. Eğer 3'ü geçerse tekrar 0'a (Başa) dön! (ROUND ROBIN MANTIĞI)
    SIRADAKI_SUNUCU_INDEX = (SIRADAKI_SUNUCU_INDEX + 1) % len(SUNUCULAR)
    
    # 3. Müşterinin isteğini alıp Hedef Sunucuya (Gizlice) yolluyoruz (Reverse Proxy)
    async with httpx.AsyncClient() as client:
        try:
            cevap = await client.get(hedef_sunucu)
            return cevap.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail=f"Hedef Sunucu ({hedef_sunucu}) şu an çökmüş durumda!")

if __name__ == "__main__":
    # Müşterilerin muhatap olacağı tek adres burasıdır (Port 8000)
    print("🚦 Trafik Polisi (Load Balancer) Başlatılıyor... Müşterileri Bekliyor.")
    uvicorn.run("load_balancer:app", host="127.0.0.1", port=8000)
