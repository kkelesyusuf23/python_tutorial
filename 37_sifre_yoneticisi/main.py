from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from sifre_motoru import sifre_kaydet, sifreleri_getir

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    # Sayfa ilk açıldığında ekranda ne mesaj var ne de çözülmüş şifre
    return templates.TemplateResponse("index.html", {"request": request, "mesaj": None, "cozulmusler": None})


@app.post("/ekle", response_class=HTMLResponse)
async def sifre_ekle(
    request: Request, 
    ana_sifre: str = Form(...), 
    platform: str = Form(...), 
    gizli_sifre: str = Form(...)
):
    """ HTML Formundan gelen verileri alıp Kriptografi motoruna şifreleten rota """
    mesaj = ""
    try:
        sifre_kaydet(ana_sifre, platform, gizli_sifre)
        mesaj = f"✅ {platform} başarıyla şifrelendi (E2EE) ve kasaya kilitlendi!"
    except Exception as e:
        mesaj = f"❌ Hata oluştu: {str(e)}"
        
    return templates.TemplateResponse("index.html", {"request": request, "mesaj": mesaj, "cozulmusler": None})


@app.post("/coz", response_class=HTMLResponse)
async def sifre_coz(request: Request, ana_sifre: str = Form(...)):
    """ Kullanıcının girdiği ana şifreyi kullanarak veritabanındaki (JSON) kilitleri kırmaya çalışan rota """
    mesaj = ""
    cozulmusler = None
    try:
        # Kriptografi motoru verileri çözer (Decrypt)
        cozulmusler = sifreleri_getir(ana_sifre)
        if not cozulmusler:
            mesaj = "⚠️ Kasanda henüz hiç şifre yok."
        else:
            mesaj = "🔓 Şifreler başarıyla çözüldü!"
            
    except ValueError:
        # Motor "Ana Şifre Yanlış" derse ValueError fırlatır
        mesaj = "🚨 YANLIŞ ANA ŞİFRE! Veritabanı şifreleri çözülemedi."
    except Exception as e:
        mesaj = f"❌ Beklenmedik Hata: {str(e)}"
        
    return templates.TemplateResponse("index.html", {"request": request, "mesaj": mesaj, "cozulmusler": cozulmusler})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
