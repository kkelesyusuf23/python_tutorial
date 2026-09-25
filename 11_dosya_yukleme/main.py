from fastapi import FastAPI, Request, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import os

app = FastAPI()

# Şablonlarımızın nerede olduğunu gösteriyoruz
templates = Jinja2Templates(directory="sablonlar")

# ==========================================================
# ADIM 6: YÜKLENEN DOSYALARI DIŞ DÜNYAYA AÇMAK (StaticFiles)
# ==========================================================
# İnsanlar yükledikleri resimleri tarayıcıda görebilsin diye 'yuklenenler' 
# klasörünü '/dosyalar' linki üzerinden internete açıyoruz.
app.mount("/dosyalar", StaticFiles(directory="yuklenenler"), name="dosyalar")

@app.get("/")
def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/yukle")
def yukle(dosya: UploadFile):
    # 1. Dosya Türü Kontrolü (Sadece resimlere izin veriyoruz)
    if dosya.content_type != "image/jpeg" and dosya.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Sadece JPG veya PNG resimleri yükleyebilirsiniz!")
        
    # 2. Dosyanın kaydedileceği yolu belirliyoruz
    kaydedilecek_yer = f"yuklenenler/{dosya.filename}"
    
    # 3. Dosyayı fiziksel olarak diske yazıyoruz
    try:
        with open(kaydedilecek_yer, "wb") as disk_dosyasi:
            shutil.copyfileobj(dosya.file, disk_dosyasi)
    except Exception:
        raise HTTPException(status_code=500, detail="Dosya kaydedilirken bir hata oluştu")
    finally:
        dosya.file.close() # RAM'i temizle
        
    # Başarılı olduğunda, yüklenen dosyanın görüntülenebileceği linki (URL) de döndürüyoruz
    resim_linki = f"/dosyalar/{dosya.filename}"
    return {
        "mesaj": "Harika! Dosya başarıyla yüklendi.", 
        "dosya_adi": dosya.filename,
        "resmi_goruntule": resim_linki
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 