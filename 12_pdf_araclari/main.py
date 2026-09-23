from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pypdf import PdfWriter, PdfReader
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Geçici dosyaları (çıktıları) kaydetmek için klasör
os.makedirs("gecici", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/birlestir")
def pdf_birlestir(dosyalar: list[UploadFile] = File(...)):
    # 1. Yeni bir PDF oluşturucu açıyoruz
    birlesik_pdf = PdfWriter()
    
    # 2. Bize gönderilen tüm dosyaları döngüye alıyoruz
    for dosya in dosyalar:
        # Sadece PDF'leri kabul edelim
        if dosya.content_type != "application/pdf":
            continue
            
        # Dosyanın içindeki baytları PdfReader'a veriyoruz
        okuyucu = PdfReader(dosya.file)
        birlesik_pdf.append(okuyucu)
        
    # 3. Sonucu fiziksel olarak diske yazıyoruz
    cikti_yolu = "gecici/birlesik.pdf"
    with open(cikti_yolu, "wb") as f:
        birlesik_pdf.write(f)
        
    # 4. Dosyayı kullanıcıya "İndirme" (Download) olarak geri gönderiyoruz!
    return FileResponse(cikti_yolu, filename="birlesik_sonuc.pdf", media_type="application/pdf")

@app.post("/filigranla")
def pdf_filigranla(dosyalar: list[UploadFile] = File(...)):
    # 1. Damgayı hazırla
    filigran = PdfReader("filigran.pdf").pages[0]
    yeni_pdf = PdfWriter()
    
    for dosya in dosyalar:
        if dosya.content_type != "application/pdf":
            continue
            
        okuyucu = PdfReader(dosya.file)
        # 2. Her dosyanın sayfalarını tek tek dolaş
        for sayfa in okuyucu.pages:
            # Sayfanın üzerine filigranı bas
            sayfa.merge_page(filigran)
            yeni_pdf.add_page(sayfa)
            
    # 3. Diske yaz
    cikti_yolu = "gecici/filigranli.pdf"
    with open(cikti_yolu, "wb") as f:
        yeni_pdf.write(f)
        
    # 4. Dosyayı indir
    return FileResponse(cikti_yolu, filename="filigranli_sonuc.pdf", media_type="application/pdf")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
