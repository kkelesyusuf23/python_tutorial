import qrcode
import io
import base64
import uuid
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="QR Bilet API")
templates = Jinja2Templates(directory="sablonlar")

# Gerçek dünyada bu veriler Postgresql gibi bir veritabanında tutulur
VERITABANI_BILETLER = {}

def karekod_olustur(veri: str) -> str:
    """
    İçine verilen metni (Link veya ID) bir QR Kod (Resim) dosyasına dönüştürür.
    HTML'de doğrudan gösterebilmek için resmi Base64 metnine çevirir.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(veri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    
    # Resmi hard diske kaydetmek yerine RAM'de (BytesIO) tutup Base64'e çeviriyoruz
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_resim = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64_resim}"


@app.get("/", response_class=HTMLResponse)
def anasayfa():
    return HTMLResponse("""
    <body style="font-family:sans-serif; text-align:center; margin-top:50px;">
        <h1>Etkinlik Biletleme API</h1>
        <a href="/bilet_al" style="padding:15px 30px; background:blue; color:white; text-decoration:none; border-radius:10px; font-weight:bold;">🎫 Yeni Bilet Satın Al</a>
    </body>
    """)


@app.get("/bilet_al", response_class=HTMLResponse)
def bilet_al(request: Request):
    """ Müşteri bilet aldığında tetiklenen rota """
    # 1. Dünyada eşi benzeri olmayan (Kriptografik) bir bilet ID'si üret
    bilet_id = str(uuid.uuid4())
    
    # 2. Veritabanına kaydet ve kullanıldı mı (False) olarak işaretle
    VERITABANI_BILETLER[bilet_id] = {"kullanildi_mi": False}
    
    # 3. Güvenlik görevlisinin okutacağı LİNKİ oluştur ve bunu QR Koda dönüştür!
    dogrulama_linki = f"http://127.0.0.1:8000/dogrula/{bilet_id}"
    qr_base64 = karekod_olustur(dogrulama_linki)
    
    return templates.TemplateResponse("bilet.html", {
        "request": request, 
        "qr_kod": qr_base64, 
        "bilet_id": bilet_id
    })


@app.get("/dogrula/{bilet_id}", response_class=HTMLResponse)
def dogrula(request: Request, bilet_id: str):
    """ Kapıdaki güvenlik görevlisi QR Kodu telefona okuttuğunda tetiklenen rota (Scanner) """
    
    mesaj = ""
    renk = ""
    durum = ""
    
    if bilet_id not in VERITABANI_BILETLER:
        mesaj = "SAHTE BİLET!"
        durum = "Sistemde böyle bir bilet numarası (UUID) bulunamadı. Lütfen polisi arayın."
        renk = "#ef4444" # Kırmızı
        
    elif VERITABANI_BILETLER[bilet_id]["kullanildi_mi"] == True:
        mesaj = "ZATEN KULLANILMIŞ BİLET!"
        durum = "Bu biletle daha önce giriş yapılmış. Lütfen müşteriyi içeri almayın."
        renk = "#f59e0b" # Turuncu
        
    else:
        # Bilet gerçek ve kullanılmamışsa: Veritabanında KULLANILDI olarak işaretle!
        VERITABANI_BILETLER[bilet_id]["kullanildi_mi"] = True
        mesaj = "BAŞARILI! KAPI AÇILIYOR..."
        durum = "Bilet geçerli. İyi eğlenceler dileriz."
        renk = "#10b981" # Yeşil
        
    return templates.TemplateResponse("dogrula.html", {
        "request": request, 
        "mesaj": mesaj, 
        "durum": durum,
        "renk": renk,
        "bilet_id": bilet_id
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
