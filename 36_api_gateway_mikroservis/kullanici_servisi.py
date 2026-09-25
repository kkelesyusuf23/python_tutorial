from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Kullanıcı Mikroservisi")

@app.get("/kullanicilar")
async def kullanici_getir():
    # Kendi bağımsız veritabanına bağlandığını hayal et
    return [
        {"id": 1, "isim": "Yusuf Keleş", "rol": "Admin"},
        {"id": 2, "isim": "Ahmet Yılmaz", "rol": "Üye"}
    ]

@app.get("/saglik")
async def saglik_kontrolu():
    return {"durum": "Kullanıcı Servisi Ayakta!"}

if __name__ == "__main__":
    # DİKKAT: Bu mikroservis sadece 8002 portunda çalışır
    uvicorn.run("kullanici_servisi:app", host="127.0.0.1", port=8002, reload=True)
