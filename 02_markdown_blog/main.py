from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import markdown
from fastapi import Request
import os

app = FastAPI()
sablon_motoru = Jinja2Templates(directory="sablonlar")








@app.get("/")
def ana_sayfa(istek: Request):
    # yazilar klasöründeki tüm dosyaların listesini al
    dosyalar = os.listdir("yazilar")
    
    # sadece '.md' uzantılı olanların isimlerini (uzantısız) topla
    yazi_isimleri = []
    for dosya in dosyalar:
        if dosya.endswith(".md"):
            isim = dosya.replace(".md", "")
            yazi_isimleri.append(isim)
            
    # Bu listeyi index.html şablonuna gönder
    return sablon_motoru.TemplateResponse("index.html", {"request": istek, "yazilar": yazi_isimleri})


@app.get("/yazi/{dosya_adi}")
def yazi_oku(istek: Request, dosya_adi: str):
    # Parametreden gelen ismin sonuna .md ekleyip dosyayı bul
    dosya_yolu = f"yazilar/{dosya_adi}.md"
    
    # Dosyayı oku ve HTML'e çevir
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        okunan_metin = dosya.read()
    
    cevrilmis_html = markdown.markdown(okunan_metin)
    
    # Yeni bir şablona (yazi.html) çevrilmiş kodu gönder
    return sablon_motoru.TemplateResponse("yazi.html", {"request": istek, "icerik": cevrilmis_html})


    