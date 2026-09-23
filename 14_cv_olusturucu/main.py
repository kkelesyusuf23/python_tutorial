from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from xhtml2pdf import pisa
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

os.makedirs("gecici", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def form_sayfasi(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/cv-olustur")
def cv_uret(
    request: Request,
    ad_soyad: str = Form(...),
    meslek: str = Form(...),
    telefon: str = Form(...),
    eposta: str = Form(...),
    hakkimda: str = Form(...),
    deneyim: str = Form(...),
    egitim: str = Form(...)
):
    taslak = templates.get_template("cv_taslak.html")
    html_metni = taslak.render({
        "ad_soyad": ad_soyad,
        "meslek": meslek,
        "telefon": telefon,
        "eposta": eposta,
        "hakkimda": hakkimda,
        "deneyim": deneyim,
        "egitim": egitim
    })

    pdf_yolu = f"gecici/cv_{ad_soyad.replace(' ', '_')}.pdf"
    
    # xhtml2pdf (pisa) kütüphanesi Mac çekirdeğine ihtiyaç duymadan
    # doğrudan Python içinden HTML'i PDF'e çevirir (Pure Python).
    with open(pdf_yolu, "wb") as pdf_dosyasi:
        pisa.CreatePDF(html_metni, dest=pdf_dosyasi)

    return FileResponse(pdf_yolu, filename=f"{ad_soyad}_Ozgecmis.pdf", media_type="application/pdf")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
