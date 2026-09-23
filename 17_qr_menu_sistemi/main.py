from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import qrcode
import uvicorn
import os
import socket

app = FastAPI()
templates = Jinja2Templates(directory="sablonlar")

# Üretilen QR kodları (resimleri) HTML'de gösterebilmek için 'statik' klasörünü dışa açıyoruz (mount)
app.mount("/statik", StaticFiles(directory="statik"), name="statik")

# ==========================================
# YEREL IP ADRESİ BULUCU (CİHAZLAR ARASI ERİŞİM İÇİN)
# ==========================================
# Eğer QR koda "http://127.0.0.1" yazarsak, telefon kamerası bunu açtığında kendi içindeki 
# yerel sunucuyu arar ve sayfayı bulamaz. Telefonun BİLGİSAYARA bağlanabilmesi için 
# bilgisayarın modemdeki (Wi-Fi) kimlik numarasını (Örn: 192.168.1.35) bilmemiz gerekir.
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()


# ==========================================
# ADMİN PANELİ: QR KOD ÜRETME ROTASI
# ==========================================
@app.get("/admin", response_class=HTMLResponse)
def admin_sayfasi(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/qr-uret")
def qr_kod_uret(request: Request, masa_no: str = Form(...)):
    # 1. Telefonun kamerası karekodu okuduğu an gitmesi gereken LİNK (Dinamik IP kullanıyoruz)
    # Örnek: http://192.168.1.35:8000/menu?masa=5
    hedef_link = f"http://{LOCAL_IP}:8000/menu?masa={masa_no}"
    
    # 2. qrcode kütüphanesi ile linki karekod (resim) objesine dönüştürüyoruz
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(hedef_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 3. Oluşan resmi statik klasörüne bilgisayarımıza (png olarak) kaydediyoruz
    dosya_adi = f"masa_{masa_no}_qr.png"
    dosya_yolu = f"statik/{dosya_adi}"
    img.save(dosya_yolu)
    
    # 4. Admin sayfasına resmi ve linki geri yolluyoruz
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "qr_resim": f"/{dosya_yolu}",
        "hedef_link": hedef_link,
        "masa_no": masa_no
    })


# ==========================================
# MÜŞTERİ PANELİ: TELEFONDAN AÇILACAK DİJİTAL MENÜ
# ==========================================
@app.get("/menu", response_class=HTMLResponse)
def musteri_menu(request: Request, masa: str = "Bilinmiyor"):
    # Telefonla okutulan karekod, müşteriyi doğrudan bu rotaya atacaktır.
    return templates.TemplateResponse("menu.html", {"request": request, "masa_no": masa})


if __name__ == "__main__":
    # DİKKAT: host="0.0.0.0" komutu HASSAS bir komuttur! 
    # Sunucumuzu sadece kendi bilgisayarımıza değil, aynı Wi-Fi ağına bağlı TÜM CİHAZLARA (Telefon, Tablet vb.) açar.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
