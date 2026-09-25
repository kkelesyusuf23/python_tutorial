from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Sipariş Mikroservisi")

@app.get("/siparisler")
async def siparis_getir():
    # Kendi bağımsız veritabanına bağlandığını hayal et
    return [
        {"id": 101, "urun": "MacBook Pro", "tutar": 2000},
        {"id": 102, "urun": "iPhone 15", "tutar": 1000}
    ]

@app.get("/saglik")
async def saglik_kontrolu():
    return {"durum": "Sipariş Servisi Ayakta!"}

if __name__ == "__main__":
    # DİKKAT: Bu mikroservis sadece 8001 portunda çalışır
    uvicorn.run("siparis_servisi:app", host="127.0.0.1", port=8001, reload=True)
